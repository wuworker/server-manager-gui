"""
Create by wuxingle on 2018/12/5
简易终端
"""
import queue
import threading
from io import BytesIO
from tkinter import *
from tkinter import ttk

import pexpect

from servergui import logger

log = logger.get(__name__)


class TerminalUI(ttk.Frame):
    """
    同步的终端
    """

    def __init__(self, master=None, cmd_handle=None, **kw):
        """
        cmd_handle: 为命令的处理函数,
                    输入为命令，输出为结果
        """
        super().__init__(master, **kw)
        self.cmd_handle = cmd_handle
        self.__create_widgets()

    def __create_widgets(self):
        self.content = Text(self, wrap='none')
        self.txt_cmd_var = StringVar()
        self.txt_cmd = ttk.Entry(self, textvariable=self.txt_cmd_var)
        self.btn_send = ttk.Button(self, text='发送')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.content.grid(row=0, column=0, columnspan=2, sticky=(N, S, W, E), pady=5)
        self.txt_cmd.grid(row=1, column=0, sticky=(N, S, W, E), pady=5)
        self.btn_send.grid(row=1, column=1, sticky=(N, S, E), pady=5)
        self.content['state'] = 'disabled'

        def send_cmd(*args):
            if not callable(self.cmd_handle):
                log.warning('the cmd_handle is not callable:%s', self.cmd_handle)
                return
            try:
                res = self.cmd_handle(self.txt_cmd_var.get())
                if res:
                    self.add_content(res)
            except Exception as e:
                log.exception('handle cmd error:%s', e)
            self.txt_cmd_var.set('')

        self._bind_send_cmd(send_cmd)

    def _bind_send_cmd(self, func):
        """
        绑定按钮和回车需要执行的函数
        """
        self.btn_send['command'] = func
        self.txt_cmd.bind('<Return>', func)

    def add_content(self, text):
        """
        往终端添加内容
        :param text: 内容
        """
        self.content['state'] = 'normal'
        self.content.insert('end', text)
        self.content.see('end -1 lines')
        self.content['state'] = 'disabled'


class AsyncTerminalUI(TerminalUI):
    """
    异步执行命令的终端UI
    通过队列进行数据传递
    """
    # 更新终端界面的事件
    __UPDATE_CMD_RESULT_EVENT = "<<CmdHasReturn>>"

    def __init__(self, master=None, cmd_handle=None, **kw):
        super().__init__(master, cmd_handle, **kw)
        self._cmd_queue = queue.Queue()
        self._result_queue = queue.Queue()
        self.bind(AsyncTerminalUI.__UPDATE_CMD_RESULT_EVENT, self.__handle_update_event)

        def btn_send(*args):
            """
            把命令发送到_cmd_queue
            """
            if self._cmd_queue.empty():
                cmd = self.txt_cmd_var.get()
                self._cmd_queue.put_nowait(cmd)
            else:
                log.warning('_cmd_queue not empty,please wait to consume cmd')

        self._bind_send_cmd(btn_send)
        self.running = False
        self.terminal = True

    def start(self):
        """
        启动线程,监听_cmd_queue队列,
        把执行结果放入_result_queue队列,通知更新
        """
        if not self.running and self.terminal:
            # 保证队列为空
            while not self._cmd_queue.empty():
                self._cmd_queue.get_nowait()
            while not self._result_queue.empty():
                self._result_queue.get_nowait()

            self.running = True
            self.terminal = False
            t = threading.Thread(target=self.__async_handle, name='CmdHandlerThread')
            t.setDaemon(True)
            t.start()
        else:
            log.warning("the CmdHandlerThread is already start!running:%s,terminal:%s",
                        self.running, self.terminal)

    def stop(self, force=False):
        if self.running:
            self.running = False
            self.txt_cmd['state'] = 'disabled'
            self.btn_send['state'] = 'disabled'
            self._cmd_queue.put_nowait(None)
        elif not force:
            log.warning('the CmdHandlerThread is already stopped or maybe stopping.terminal:%s', self.terminal)

    def __handle_update_event(self, event):
        """
        处理内容更新事件
        从_result_queue队列获取结果，进行更新
        """
        try:
            content = self._result_queue.get_nowait()
            self.txt_cmd_var.set('')
            self.add_content(content)
        except queue.Empty as e:
            log.exception('can not update content:%s', e)

    def __async_handle(self, *args):
        """
        从_cmd_queue队列获取命令
        处理完后异步更新
        """
        try:
            self._async_handle_before()
            while self.running:
                cmd = self._cmd_queue.get()
                if cmd is None:
                    continue
                try:
                    res = self.cmd_handle(cmd)
                    log.debug('handle cmd:"%s",result:%s', cmd, 'None' if res is None else res.encode('utf-8'))
                    if res is not None:
                        self.add_content_async(res)
                except Exception as e:
                    log.exception('handle cmd "%s" error:%s', cmd, e)
                    self.add_content_async(self._format_error(e))
            self._async_handle_after()
        except Exception as e:
            log.exception('before or after handle cmd error:%s', e)
            self.stop(True)
            self.add_content_async(self._format_error(e))
        finally:
            self.terminal = True
            log.info('the cmd handle thread is stopped')

    def _format_error(self, e):
        return e.__str__()

    def _async_handle_before(self):
        pass

    def _async_handle_after(self):
        pass

    def add_content_async(self, text):
        """
        往终端异步添加内容
        :param text: 内容
        """
        self._result_queue.put(text)
        self.event_generate(AsyncTerminalUI.__UPDATE_CMD_RESULT_EVENT)


class InteractiveTerminalUI(AsyncTerminalUI):
    """
    交互式类型的终端
    使用pexpect
    """

    def __init__(self, master=None, cmd_start=None, expects=None, timeout=10, **kw):
        """
        :param cmd_start: 启动交互式的一连串命令和预期结果
        :param expects: 每次命令的返回预期
        :param timeout: 超时时间，秒
        """
        self.cmd_start = cmd_start
        self.expects = expects
        self.timeout = timeout
        self.__p = None
        self.__f = None

        def cmd_handle(cmd):
            try:
                return self.__send_and_expect(cmd, self.expects)
            except pexpect.EOF as e:
                return self._format_error(e)

        super().__init__(master, cmd_handle, **kw)

    def _async_handle_before(self):
        """
        启动交互式shell
        """
        self.add_content_async(self.cmd_start[0] + "\n")
        p = self.__p = pexpect.spawn(self.cmd_start[0])
        f = self.__f = BytesIO()
        p.logfile_read = f
        res = self.__expect_and_return(self.cmd_start[1])
        self.add_content_async(res)
        cmd_it = iter(self.cmd_start)
        next(cmd_it)
        next(cmd_it)
        while True:
            try:
                res = self.__send_and_expect(next(cmd_it), next(cmd_it))
                self.add_content_async(res)
            except StopIteration:
                break

    def _async_handle_after(self):
        self.__p.close()
        self.__f.close()

    def _format_error(self, e):
        return super()._format_error(e) if not hasattr(e, 'last_output') else e.last_output

    def __send_and_expect(self, cmd, expect):
        self.__f.seek(0)
        self.__p.sendline(cmd)
        return self.__expect_and_return(expect)

    def __expect_and_return(self, expect):
        try:
            self.__p.expect(expect, timeout=self.timeout)
            size = self.__f.tell()
            self.__f.seek(0)
            return self.__f.read(size).decode('utf-8')
        except pexpect.EOF as e:
            size = self.__f.tell()
            self.__f.seek(0)
            res = self.__f.read(size).decode('utf-8')
            self.stop(True)
            e.last_output = res
            raise e
        except pexpect.TIMEOUT as e:
            raise e

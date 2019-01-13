"""
Create by wuxingle on 2018/12/5
命令处理和简易终端

在调用stop时,对状态的修改还未进行同步
"""
import queue
import subprocess
import threading
from io import BytesIO
from subprocess import signal
from tkinter import *
from tkinter import ttk
from typing import List

import pexpect

from servergui import logger

log = logger.get(__name__)


class AsyncShell:
    def __init__(self, async_name, cmd):
        """
        异步处理命令的抽象类
        :param async_name: 异步线程名
        :param cmd: 命令
        """
        self.async_name = async_name
        self.cmd = cmd
        self.running = False
        self.terminal = True

    def start(self):
        if self.terminal and not self.running:
            self.running = True
            self.terminal = False
            t = threading.Thread(target=self.__task, name=self.async_name)
            t.setDaemon(True)
            t.start()
        else:
            log.warning("the '%s' can not start!running:%s,terminal:%s", self.async_name, self.running, self.terminal)

    def stop(self, force=False):
        self.running = False

    def wrapper_handle(self, func, error_handle=None):
        """
        handler装饰器
        只有running为true才处理
        """

        def wrapper(*args, **kw):
            try:
                if self.running:
                    func(*args, **kw)
            except Exception as e:
                log.exception("'%s' handle error:%s", self.async_name, e)
                if callable(error_handle):
                    error_handle(e)

        return wrapper

    def _handle_cmd(self):
        pass

    def __task(self):
        """
        处理命令的异步任务
        """
        log.info("exc '%s' start", self.cmd)
        try:
            self._handle_cmd()
        finally:
            log.info("exec '%s' end", self.cmd)
            self.running = False
            self.terminal = True


class NormalShell(AsyncShell):
    """
    普通的shell,执行完能直接结束
    """

    def __init__(self, cmd, handler, error_handler=None, timeout=20):
        """
        :param handler: 命令结果回调，参数为(code,bytes)
        :param timeout:
        """
        super().__init__('NormalShellThread', cmd)
        self.handler = self.wrapper_handle(handler, error_handler)
        self.timeout = timeout
        self.__p: subprocess.Popen = None

    def stop(self, force=False):
        super().stop(force)
        if not self.terminal and self.__p is not None:
            s = signal.SIGKILL if force else signal.SIGTERM
            self.__p.send_signal(s)

    def _handle_cmd(self):
        try:
            self.__p = p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, shell=True)
            log.info("exec '%s', pid :%s", self.cmd, p.pid)
            p.wait(timeout=self.timeout)
            code = p.returncode
            lines_bytes = p.stdout.read() if code == 0 else p.stderr.read()
            self.handler(code, lines_bytes)
        except Exception as e:
            log.exception("exec '%s' error", e)
            if self.__p is not None:
                if self.__p.poll() is None:
                    self.__p.send_signal(signal.SIGKILL)
        finally:
            self.__p = None


class LoopShell(AsyncShell):
    """
    无法自动停止的命令，比如tail -f
    """

    def __init__(self, cmd, handler, error_handler=None):
        """
        :param handler: 命令结果回调，参数为(code,bytes)
        """
        super().__init__('LoopShellThread', cmd)
        self.handler = self.wrapper_handle(handler, error_handler)
        self.__p: subprocess.Popen = None

    def stop(self, force=False):
        super().stop(force)
        if not self.terminal and self.__p is not None:
            s = signal.SIGKILL if force else signal.SIGTERM
            self.__p.send_signal(s)

    def _handle_cmd(self):
        try:
            self.__p = p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, shell=True)
            log.info("exec '%s', pid :%s", self.cmd, p.pid)
            while p.poll() is None:
                line = p.stdout.readline()
                code = p.poll()
                if code:
                    if code != 0:
                        line = p.stderr.read()
                        self.handler(code, line)
                    break
                self.handler(0, line)

        except Exception as e:
            log.exception("exec '%s' error", e)
            if self.__p is not None and self.__p.poll() is None:
                self.__p.send_signal(signal.SIGKILL)
        finally:
            self.__p = None


class InteractiveShell(AsyncShell):
    """
    交互式的命令，比如telnet
    """

    def __init__(self, cmd_start, expects: List[str], handle, error_handle=None, timeout=10):
        """
        :param cmd_start: 初始命令
        :param expects: [expect,send,...,expect]
        :param handle: 命令结果回调(str)
        """
        super().__init__('InteractiveShellThread', cmd_start)
        self.final_expect = expects[-1]
        self.expects = expects
        self.handle = self.wrapper_handle(handle, error_handle)
        self.timeout = timeout
        self._cmd_queue = queue.Queue()
        self.__p: pexpect.spawn = None
        self.__f: BytesIO = None

    def start(self):
        while not self._cmd_queue.empty():
            self._cmd_queue.get_nowait()
        super().start()

    def stop(self, force=False):
        super().stop(force)
        if not self.terminal:
            self._cmd_queue.put_nowait(None)
            if self.__p is not None and not self.__p.closed:
                self.__p.close()
                self.__p = None
            if self.__f is not None and not self.__f.closed:
                self.__f.close()
                self.__f = None

    def exec_cmd(self, cmd):
        if not self.running:
            raise RuntimeError('the interactive shell thread not start!')
        self._cmd_queue.put(cmd)

    def _handle_cmd(self):
        try:
            p = self.__p = pexpect.spawn(self.cmd)
            f = self.__f = BytesIO()
            p.logfile_read = f

            for i in range(0, len(self.expects) + 1, 2):
                res = self.__wait_expect(self.expects[i])
                self.handle(res)
                if i + 1 < len(self.expects):
                    self.__send_cmd(self.expects[i + 1])

            log.info("exec '%s' start interactive", self.cmd)
            while self.running:
                cmd = self._cmd_queue.get()
                if cmd is None:
                    continue
                self.__send_cmd(cmd)
                res = self.__wait_expect(self.final_expect)

                log.debug('handle cmd:"%s",result:%s', cmd, 'None' if res is None else res.encode('utf-8'))
                if res is not None:
                    self.handle(res)
        except pexpect.EOF:
            size = self.__f.tell()
            self.__f.seek(0)
            res = self.__f.read(size).decode('utf-8')
            self.handle(res)
        except pexpect.ExceptionPexpect as e:
            self.handle(str(e))
        finally:
            if self.running:
                if self.__p is not None and not self.__p.closed:
                    self.__p.close()
                    self.__p = None
                if self.__f is not None and not self.__f.closed:
                    self.__f.close()
                    self.__f = None

    def __send_cmd(self, cmd):
        self.__f.seek(0)
        self.__p.sendline(cmd)

    def __wait_expect(self, expect):
        self.__p.expect(expect, timeout=self.timeout)
        size = self.__f.tell()
        self.__f.seek(0)
        return self.__f.read(size).decode('utf-8')


class BaseTerminalUI(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.content = Text(self, wrap='none')
        self.content['state'] = 'disabled'

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def start(self):
        pass

    def add_content(self, text):
        """
        往终端添加内容
        :param text: 内容
        """
        self.content['state'] = 'normal'
        self.content.insert('end', text)
        self.content.see('end -1 lines')
        self.content['state'] = 'disabled'


class NormalTerminalUI(BaseTerminalUI):
    """
    normal类型的命令，结果使用text显示
    """

    def __init__(self, master=None, cmd=None, timeout=20, **kw):
        super().__init__(master, **kw)

        self.add_content('> ' + cmd + '\n')
        self.content.grid(row=0, column=0, sticky=(N, S, W, E))

        self.normalShell = NormalShell(cmd, lambda code, line: self.add_content(line), timeout=timeout)

    def start(self):
        self.normalShell.start()

    def destroy(self):
        self.normalShell.stop()
        super().destroy()


class LoopTerminalUI(BaseTerminalUI):
    """
    loop类型的命令，结果使用text显示
    """

    def __init__(self, master=None, cmd=None, **kw):
        super().__init__(master, **kw)

        self.add_content('> ' + cmd + '\n')
        self.content.grid(row=0, column=0, sticky=(N, S, W, E))

        self.loopShell = LoopShell(cmd, lambda code, line: self.add_content(line))

    def start(self):
        self.loopShell.start()

    def destroy(self):
        self.loopShell.stop()
        super().destroy()


class InteractiveTerminalUI(BaseTerminalUI):
    """
    交互式命令的终端
    """

    def __init__(self, master=None, cmd_start=None, expects: List[str] = None, **kw):
        """
        cmd_handle: 为命令的处理函数,
                    输入为命令，输出为结果
        """
        super().__init__(master, **kw)
        self.txt_cmd_var = StringVar()
        self.txt_cmd = ttk.Entry(self, textvariable=self.txt_cmd_var)
        self.btn_send = ttk.Button(self, text='发送')

        self.content.grid(row=0, column=0, columnspan=2, sticky=(N, S, W, E), pady=5)
        self.txt_cmd.grid(row=1, column=0, sticky=(N, S, W, E), pady=5)
        self.btn_send.grid(row=1, column=1, sticky=(N, S, E), pady=5)

        def send_cmd(*args):
            if self.interShell.running:
                self.interShell.exec_cmd(self.txt_cmd_var.get())
                self.txt_cmd_var.set('')
            else:
                self.btn_send['state'] = 'disabled'
                self.txt_cmd['state'] = 'disabled'

        self.btn_send['command'] = send_cmd
        self.txt_cmd.bind('<Return>', send_cmd)

        self.interShell = InteractiveShell(cmd_start, expects, lambda s: self.add_content(s))

    def start(self):
        self.interShell.start()

    def destroy(self):
        self.interShell.stop()
        super().destroy()

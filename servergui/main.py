"""
Create by wuxingle on 2018/12/3
服务管理界面
"""

from servergui.termwidgets import *
from servergui import logger

log = logger.get(__name__)


class CmdData:
    TYPE_OF_NORMAL = 0
    TYPE_OF_LOOP = 1
    TYPE_OF_INTERACTIVE = 2

    def __init__(self, name, cmd, tp, expects=None):
        self.name = name
        self.cmd = cmd
        self.tp = tp
        self.expects = expects

    def __str__(self):
        return 'name:%s,cmd:%s,tp:%s,expects:%s' % (self.name, self.cmd, self.tp, self.expects)

    __repr__ = __str__


class ServerData:
    def __init__(self, title, status_cmd, btn_list):
        self.title = title
        self.status_cmd = status_cmd
        self.btn_list = btn_list

    def __str__(self):
        return 'title:%s,status_cmd:%s,btn_list:%s' % (self.title, self.status_cmd, self.btn_list)

    __repr__ = __str__


class MainUI(ttk.Frame):
    def __init__(self, master=None, datas=None, **kw):
        super().__init__(master, **kw)
        self.datas = datas

        # 服务列表
        server_list = list(map(lambda d: d.title, datas))
        print(server_list)

        # 左边
        btn_add = ttk.Button(self, text='➕')
        btn_sub = ttk.Button(self, text='➖')

        lbox_var = StringVar(value=server_list)
        self.lbox = Listbox(self, listvariable=lbox_var)
        self.lbox['relief'] = 'sunken'

        btn_add.grid(row=0, column=0, sticky=(N, W, E))
        btn_sub.grid(row=0, column=1, sticky=(N, W, E))
        self.lbox.grid(row=1, column=0, columnspan=2, sticky=(N, W, E, S), padx=5)
        self.lbox.bind('<<ListboxSelect>>', self.__listbox_select)

        # 初始化右边按钮
        self.frames = []
        for data in datas:
            fra = self.__create_frame(data)
            self.frames.append(fra)

        self.last_select = -1

        self.lbox.select_set(0)
        self.__listbox_select()

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def __create_frame(self, data) -> ttk.Frame:
        fra = ttk.Frame(self)

        lab_title = ttk.Label(fra, text=data.title, anchor=CENTER)
        lab_status = ttk.Label(fra, text='running', anchor=CENTER)
        btn_fresh = ttk.Button(fra, text='刷新')

        lab_title.grid(row=0, column=0, columnspan=2, sticky=(W, E), padx=5, pady=10)
        lab_status.grid(row=1, column=0, sticky=(W, E), padx=5, pady=5)
        btn_fresh.grid(row=1, column=1, sticky=(W, E), padx=5, pady=5)

        i = 2
        for btn_data in data.btn_list:
            btn = ttk.Button(fra, text=btn_data.name,
                             command=self.__invoke_cmd(data.title + ' -> ' + btn_data.name, btn_data))
            btn.grid(row=i, column=0, columnspan=2, sticky=(W, E), padx=10, pady=5)
            i = i + 1

        btn_add = ttk.Button(fra, text='➕', command=self.__add_btn)
        btn_add.grid(row=i, column=0, columnspan=2, sticky=(W, E), padx=10, pady=5)

        return fra

    def __invoke_cmd(self, title, cmd_data):
        def click(*args):
            win = Toplevel()
            win.title(title)
            term = None
            if cmd_data.tp == CmdData.TYPE_OF_NORMAL:
                term = OnceTerminalUI(master=win, cmd=cmd_data.cmd)
            elif cmd_data.tp == CmdData.TYPE_OF_LOOP:
                pass
            elif cmd_data.tp == CmdData.TYPE_OF_INTERACTIVE:
                term = InteractiveTerminalUI(master=win, cmd_start=cmd_data.cmd, expects=cmd_data.expects)
            else:
                log.warning('the cmdData type is not allowed:%s', cmd_data.tp)
                return

            term.grid(row=0, column=0, sticky=(N, S, W, E))
            term.start()

        return click

    def __add_btn(self):
        pass

    def __listbox_select(self, *args):
        indices = self.lbox.curselection()
        print('select:', indices)
        if len(indices) != 1:
            return
        idx = indices[0]
        if idx == self.last_select:
            return

        self.frames[idx].grid(row=0, column=2, rowspan=2, sticky=(N, S, W, E), padx=5, pady=10)
        if self.last_select >= 0:
            self.frames[self.last_select].grid_forget()

        self.last_select = idx


if __name__ == '__main__':
    root = Tk()
    root.title('服务管理')
    root.resizable(False, False)

    mysql_list = [CmdData('启动', '/usr/local/bin/mysql.server start', CmdData.TYPE_OF_NORMAL),
                  CmdData('停止', '/usr/local/bin/mysql.server stop', CmdData.TYPE_OF_NORMAL),
                  CmdData('重启', '/usr/local/bin/mysql.server restart', CmdData.TYPE_OF_NORMAL),
                  CmdData('日志', 'ls', CmdData.TYPE_OF_LOOP),
                  CmdData('终端', ['mysql -uroot -p', 'password', '123456', 'mysql>'],
                          CmdData.TYPE_OF_INTERACTIVE, expects='>')]

    mysql_data = ServerData(title='mysql', status_cmd='ps -ef|grep mysql', btn_list=mysql_list)

    redis_list = [CmdData('启动1', 'ls', CmdData.TYPE_OF_NORMAL),
                  CmdData('停止1', 'ls', CmdData.TYPE_OF_NORMAL),
                  CmdData('重启1', 'ls', CmdData.TYPE_OF_NORMAL),
                  CmdData('日志1', 'ls', CmdData.TYPE_OF_LOOP),
                  CmdData('终端1', 'ls', CmdData.TYPE_OF_INTERACTIVE)]

    redis_data = ServerData(title='redis', status_cmd='ps -ef|grep redis', btn_list=redis_list)

    mainui = MainUI(root, datas=[mysql_data, redis_data], padding=5)
    mainui.grid(row=0, column=0, sticky=(N, S, W, E))

    root.mainloop()

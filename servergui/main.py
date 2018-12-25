"""
Create by wuxingle on 2018/12/3
服务管理界面
"""

from servergui.termwidgets import *

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

        # 下面的命令结果
        self.cmd_results = []
        self.lab_var = StringVar()
        self.lab_last_cmd = ttk.Label(self, textvariable=self.lab_var)
        self.lab_last_cmd['justify'] = LEFT

        def show_cmd_history(*args):
            if len(self.cmd_results) > 0:
                win = Toplevel()
                win.title(self.cmd_results.pop(0))
                content = Text(master=win, wrap='none')
                for cmd in self.cmd_results:
                    content.insert('end', cmd + '\n')

                content.see('end -1 lines')
                content['state'] = 'disabled'
                content.grid()

        self.lab_last_cmd.bind('<Button-1>', show_cmd_history)
        self.lab_last_cmd.grid(row=2, column=0, columnspan=3, sticky=(W, E), padx=5)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)

    def __create_frame(self, data) -> ttk.Frame:
        fra = ttk.Frame(self)

        lab_title = ttk.Label(fra, text=data.title, anchor=CENTER)
        lab_status = ttk.Label(fra, text='running', anchor=CENTER)
        btn_fresh = ttk.Button(fra, text='刷新')

        lab_title.grid(row=0, column=0, columnspan=2, sticky=(W, E), padx=5, pady=10)
        lab_status.grid(row=1, column=0, sticky=(W, E), padx=5, pady=5)
        btn_fresh.grid(row=1, column=1, sticky=(W, E), padx=5, pady=5)

        fra.rowconfigure(0, weight=1)
        fra.rowconfigure(1, weight=1)
        fra.columnconfigure(0, weight=2)
        fra.columnconfigure(1, weight=1)

        i = 2
        for btn_data in data.btn_list:
            btn = ttk.Button(fra, text=btn_data.name,
                             command=self.__invoke_cmd(data.title + ' -> ' + btn_data.name, btn_data))
            btn.grid(row=i, column=0, columnspan=2, sticky=(N, S, W, E), padx=10, pady=5)
            fra.rowconfigure(i, weight=1)
            i = i + 1

        btn_add = ttk.Button(fra, text='➕', command=self.__add_btn)
        btn_add.grid(row=i, column=0, columnspan=2, sticky=(W, E), padx=10, pady=5)
        fra.rowconfigure(i, weight=1)

        return fra

    def __invoke_cmd(self, title, cmd_data):
        def click(*args):
            # 普通的命令
            if cmd_data.tp == CmdData.TYPE_OF_NORMAL:
                def suc(code, lines):
                    print('suc', code, lines)
                    lines.insert(0, title)
                    self.show_cmd_result(lines)

                def err(e):
                    print('err', e)
                    self.show_cmd_result([title, str(e)])

                self.lab_var.set(cmd_data.cmd)
                async_shell = NormalShell(cmd_data.cmd, handler=suc, error_handler=err)
                async_shell.invoke()

            # 交互式命令
            elif cmd_data.tp == CmdData.TYPE_OF_INTERACTIVE:
                win = Toplevel()
                win.title(title)
                win.rowconfigure(0,weight=1)
                win.columnconfigure(0,weight=1)
                term = InteractiveTerminalUI(master=win, cmd_start=cmd_data.cmd, expects=cmd_data.expects)
                term.grid(row=0, column=0, sticky=(N, S, W, E))
                term.start()

            # 循环的命令
            elif cmd_data.tp == CmdData.TYPE_OF_LOOP:
                win = Toplevel()
                win.title(title)
                win.rowconfigure(0,weight=1)
                win.columnconfigure(0,weight=1)
                loop = LoopTerminalUI(master=win, cmd=cmd_data.cmd)
                loop.grid(row=0, column=0, sticky=(N, S, W, E))
                loop.start()
            else:
                log.warning('the cmdData type is not allowed:%s', cmd_data.tp)

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

    def show_cmd_result(self, cmds):
        '''
        可能需要同步
        :param cmds:
        :return:
        '''
        self.cmd_results.clear()
        for cmd in cmds:
            self.lab_var.set(cmd)
            self.cmd_results.append(cmd)


if __name__ == '__main__':
    root = Tk()
    root.title('服务管理')
    root.resizable(True, True)
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    mysql_list = [CmdData('启动', '/usr/local/bin/mysql.server start', CmdData.TYPE_OF_NORMAL),
                  CmdData('停止', '/usr/local/bin/mysql.server stop', CmdData.TYPE_OF_NORMAL),
                  CmdData('重启', '/usr/local/bin/mysql.server restart', CmdData.TYPE_OF_NORMAL),
                  CmdData('日志', 'tail -f /usr/local/var/log/mysql/error.log', CmdData.TYPE_OF_LOOP),
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

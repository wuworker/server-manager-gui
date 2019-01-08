"""
Create by wuxingle on 2018/12/3
服务管理界面
"""
from tkinter import font

import PIL.Image
from PIL import ImageTk

from servergui.dialog import *
from servergui.termwidgets import *

log = logger.get(__name__)


class CmdData:
    """
    命令对象
    """
    TYPE_OF_NORMAL = 0
    TYPE_OF_LOOP = 1
    TYPE_OF_INTERACTIVE = 2

    def __init__(self, name: str, cmd: str, tp: int, expects: List[str] = None):
        """
        :param name: 命令名称
        :param cmd: 具体命令
        :param tp: 命令类型
        :param expects: 交互式类型的预期返回等
        """
        self.name = name
        self.cmd = cmd
        self.tp = tp
        self.expects = expects

    def __str__(self):
        return 'name:%s,cmd:%s,tp:%s,expects:%s' % (self.name, self.cmd, self.tp, self.expects)

    __repr__ = __str__


class ServerData:
    """
    服务对象
    """

    def __init__(self, title: str, status_cmd: str, btn_list: List[CmdData]):
        """
        :param title: 服务名称
        :param status_cmd: 判断状态的命令
        :param btn_list: 具体的子命令
        """
        self.title = title
        self.status_cmd = status_cmd
        self.btn_list = btn_list

    def __str__(self):
        return 'title:%s,status_cmd:%s,btn_list:%s' % (self.title, self.status_cmd, self.btn_list)

    __repr__ = __str__


class ServerItemUI(ttk.Frame):

    def __init__(self, master, server_data: ServerData, active_img, dead_img, **kw):
        """
        单个服务界面
        """
        super().__init__(master, **kw)
        self.server_data = server_data
        self.active_img = active_img
        self.dead_img = dead_img

        # 标题和刷新栏
        self.title_var = StringVar(value=server_data.title)
        lab_title = ttk.Label(self, textvariable=self.title_var, anchor=CENTER, font=font.Font(size=20))
        lab_title['relief'] = 'sunken'

        self.btn_fresh = self.__create_status_btn()
        lab_title.grid(row=0, column=0, sticky=(W, E), padx=5, pady=10)
        self.btn_fresh.grid(row=0, column=1, sticky=(W, E), padx=5, pady=5)

        # 状态栏
        fra_row_1 = ttk.Frame(self)
        self.lab_status_img = ttk.Label(fra_row_1, image=self.active_img)
        self.status_var = StringVar()
        lab_status = ttk.Label(fra_row_1, textvariable=self.status_var, anchor=CENTER)

        fra_row_1.grid(row=1, column=0, columnspan=2, sticky=(W, E))
        self.lab_status_img.grid(row=0, column=0, sticky=(W,), padx=5, pady=5)
        lab_status.grid(row=0, column=1, sticky=(W, E), padx=5, pady=5)
        fra_row_1.rowconfigure(0, weight=1)
        fra_row_1.columnconfigure(1, weight=1)

        # 命令按钮
        i = 2
        for btn_data in server_data.btn_list:
            btn = self.__create_btn(btn_data)
            btn.grid(row=i, column=0, columnspan=2, sticky=(N, S, W, E), padx=10, pady=5)
            self.rowconfigure(i, weight=1)
            i = i + 1

        # 动态添加按钮
        def add_cmd_btn(*args):
            def add_cmd(cmd_data: CmdData):
                server_data.btn_list.append(cmd_data)
                b = self.__create_btn(cmd_data)
                self.max_column = self.max_column + 1
                btn_add.grid(row=self.max_column + 1, column=0, columnspan=2, sticky=(W, E), padx=10, pady=5)
                b.grid(row=self.max_column, column=0, columnspan=2, sticky=(N, S, W, E), padx=10, pady=5)

            self.show_cmd_modify_dialog('添加', add_cmd)

        btn_add = ttk.Button(self, text='➕', command=add_cmd_btn)
        btn_add.grid(row=i, column=0, columnspan=2, sticky=(W, E), padx=10, pady=5)
        self.max_column = i
        self.rowconfigure(i, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

    def __create_status_btn(self) -> ttk.Button:
        """
        创建刷新按钮
        """

        def edit(s):
            self.server_data.status_cmd = s
            self.status_refresh()

        btn = ttk.Button(self, text='刷新', width=3, command=self.status_refresh)
        btn.bind('<Button-2>', lambda *args: show_edit_dialog('编辑', self.server_data.status_cmd, edit))
        return btn

    def __create_btn(self, cmd_data: CmdData) -> ttk.Button:
        """
        创建命令按钮
        """

        # 右键按钮进行命令编辑
        def edit(*args):
            def edit_handle(new_data: CmdData):
                cmd_data.name = new_data.name
                cmd_data.tp = new_data.tp
                cmd_data.cmd = new_data.cmd
                cmd_data.expects = new_data.expects
                name_var.set(new_data.name)

            def del_btn():
                self.server_data.btn_list.remove(cmd_data)
                btn.grid_remove()

            self.show_cmd_modify_dialog('编辑', edit_handle, del_btn, cmd_data)

        name_var = StringVar(value=cmd_data.name)
        btn = ttk.Button(self, textvariable=name_var, command=self.__invoke_cmd(cmd_data))
        btn.bind('<Button-2>', edit)
        return btn

    def __invoke_cmd(self, cmd_data: CmdData):
        """
        命令按钮点击
        """

        def click(*args):
            if not cmd_data.cmd or not cmd_data.cmd.strip():
                return
            title = cmd_data.cmd
            win = Toplevel()
            win.title(title)
            win.rowconfigure(0, weight=1)
            win.columnconfigure(0, weight=1)

            # 普通的命令
            if cmd_data.tp == CmdData.TYPE_OF_NORMAL:
                term = NormalTerminalUI(master=win, cmd=cmd_data.cmd)
            # 循环的命令
            elif cmd_data.tp == CmdData.TYPE_OF_LOOP:
                term = LoopTerminalUI(master=win, cmd=cmd_data.cmd)
            # 交互式命令
            elif cmd_data.tp == CmdData.TYPE_OF_INTERACTIVE:
                term = InteractiveTerminalUI(master=win, cmd_start=cmd_data.cmd, expects=cmd_data.expects)
            else:
                log.error('the cmd data tp not allowd:%s', cmd_data)
                return

            term.grid(row=0, column=0, sticky=(N, S, W, E))
            term.start()

        return click

    def show_cmd_modify_dialog(self, title, edit_handle, del_handle=None,
                               init_data: CmdData = CmdData('', '', CmdData.TYPE_OF_NORMAL, [])):
        """
        编辑命令对话框
        :param title: 标题
        :param edit_handle: 命令处理函数
        :param del_handle:
        :param init_data: 初始化数据
        """
        win = BaseDialog(title)
        fra = win.content()

        lab_name = ttk.Label(fra, text='名称:')
        txt_name = ttk.Entry(fra)
        txt_name.insert(END, init_data.name)
        txt_name.focus_set()

        lab_type = ttk.Label(fra, text='命令类型:')
        type_var = IntVar(0)

        def cmd_radio():
            if type_var.get() == 2:
                txt_expect['state'] = 'normal'
                lab_expect['foreground'] = ''
            else:
                txt_expect['state'] = 'disabled'
                lab_expect['foreground'] = 'gray'

        type1 = ttk.Radiobutton(fra, text='普通', variable=type_var, value=CmdData.TYPE_OF_NORMAL, command=cmd_radio)
        type2 = ttk.Radiobutton(fra, text='循环', variable=type_var, value=CmdData.TYPE_OF_LOOP, command=cmd_radio)
        type3 = ttk.Radiobutton(fra, text='交互式', variable=type_var, value=CmdData.TYPE_OF_INTERACTIVE,
                                command=cmd_radio)
        type_var.set(init_data.tp)

        lab_cmd = ttk.Label(fra, text='命令:')
        txt_cmd = ttk.Entry(fra)
        txt_cmd.insert(END, init_data.cmd)

        lab_expect = ttk.Label(fra, text='预期响应:', foreground='gray')
        txt_expect = Text(fra, height=5)

        if init_data.expects is not None:
            for line in init_data.expects:
                txt_expect.insert(END, line + '\n')

        def ok(*args):
            name = txt_name.get()
            tp = type_var.get()
            c = txt_cmd.get()
            exp = txt_expect.get('1.0', END).splitlines()
            edit_handle(CmdData(name, c, tp, exp))
            win.destroy()

        btn_ok = ttk.Button(fra, text='确定', command=ok, default='active')
        cmd_radio()

        lab_name.grid(row=0, column=0, columnspan=6, sticky=(W, E))
        txt_name.grid(row=1, column=0, columnspan=6, sticky=(W, E), pady=5)
        lab_type.grid(row=2, column=0, columnspan=6, sticky=(W, E))
        type1.grid(row=3, column=0, columnspan=2, pady=5)
        type2.grid(row=3, column=2, columnspan=2, pady=5)
        type3.grid(row=3, column=4, columnspan=2, pady=5)
        lab_cmd.grid(row=4, column=0, columnspan=6, sticky=(W, E))
        txt_cmd.grid(row=5, column=0, columnspan=6, sticky=(W, E), pady=5)
        lab_expect.grid(row=6, column=0, columnspan=6, sticky=(W, E))
        txt_expect.grid(row=7, column=0, columnspan=6, sticky=(W, E, N, S), pady=5)

        if del_handle is None:
            btn_ok.grid(row=8, column=0, columnspan=6, pady=5)
        # 需要显示删除按钮
        else:
            def del_btn(*args):
                del_handle()
                win.destroy()

            btn_del = ttk.Button(fra, text='删除此按钮', command=del_btn)
            btn_ok.grid(row=8, column=0, columnspan=3, pady=5)
            btn_del.grid(row=8, column=3, columnspan=3, pady=5)

        for i in range(0, 6):
            fra.columnconfigure(i, weight=1)
        fra.rowconfigure(7, weight=1)
        win.bind('<Return>', ok)

    def set_title(self, value):
        self.server_data.title = value
        self.title_var.set(value)

    def status_refresh(self, *args):
        cmd = self.server_data.status_cmd
        if cmd and cmd.strip():
            NormalShell(cmd, handler=lambda code, lines: self.status_active() if code == 0 else self.status_dead(),
                        error_handler=lambda e: self.status_dead()).start()

    def status_active(self):
        self.status_var.set('正在运行...')
        self.lab_status_img['image'] = self.active_img

    def status_dead(self):
        self.status_var.set('已停止')
        self.lab_status_img['image'] = self.dead_img


class MainUI(ttk.Frame):

    def __init__(self, master=None, servers_data: List[ServerData] = None, **kw):
        super().__init__(master, **kw)
        self.servers_data = servers_data

        # 加载图
        self.active_img = ImageTk.PhotoImage(PIL.Image.open('../img/status_active.gif'))
        self.dead_img = ImageTk.PhotoImage(PIL.Image.open('../img/status_dead.gif'))
        self.refresh_img = ImageTk.PhotoImage(PIL.Image.open('../img/btn_refresh.gif'))

        # 左边界面
        btn_add = ttk.Button(self, text='➕', command=self.__add_server)
        btn_sub = ttk.Button(self, text='➖', command=self.__del_server)

        # 服务列表
        self.server_list = list(map(lambda d: d.title, servers_data))
        self.lbox_var = StringVar(value=self.server_list)
        self.lbox = Listbox(self, listvariable=self.lbox_var)
        self.lbox['relief'] = 'sunken'

        btn_add.grid(row=0, column=0, sticky=(N, W, E))
        btn_sub.grid(row=0, column=1, sticky=(N, W, E))
        self.lbox.grid(row=1, column=0, columnspan=2, sticky=(N, W, E, S), padx=5)
        self.lbox.bind('<<ListboxSelect>>', self.__listbox_select)
        self.lbox.bind('<Button-2>', self.__listbox_edit)
        self.lbox.bind('<Double-1>', self.__listbox_edit)

        # 初始化右边界面
        self.frames: List[ServerItemUI] = []
        for data in servers_data:
            fra = ServerItemUI(self, data, self.active_img, self.dead_img)
            self.frames.append(fra)

        self.last_select = -1
        self.select_server(0)

        # 下边界面的命令结果
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

        self.lbox.select_set(0)

    def __add_server(self):
        def handle(s):
            server_data = ServerData(s, '', [CmdData('请编辑', '', CmdData.TYPE_OF_NORMAL)])
            self.servers_data.append(server_data)
            self.server_list.append(s)
            self.lbox_var.set(self.server_list)

            fra = ServerItemUI(self, server_data, self.active_img, self.dead_img)
            fra.status_dead()
            self.frames.append(fra)
            self.select_server(len(self.server_list) - 1)

        show_edit_dialog('请输入服务名', '', handle)

    def __del_server(self):
        index = self.__current_index()
        if index < 0:
            return

        self.servers_data.pop(index)
        self.server_list.pop(index)
        self.frames.pop(index).grid_remove()

        self.lbox_var.set(self.server_list)

        if index >= len(self.server_list):
            index = index - 1

        self.last_select = -1
        self.select_server(index)

    def __listbox_edit(self, *args):
        idx = self.__current_index()
        if idx < 0 or idx >= len(self.server_list):
            return

        def edit(s):
            self.server_list[idx] = s
            self.lbox_var.set(self.server_list)
            self.frames[idx].set_title(s)

        show_edit_dialog('编辑', self.server_list[idx], edit)

    def __listbox_select(self, *args):
        """
        列表选择，切换右边的界面
        """
        idx = self.__current_index()
        if idx == self.last_select or idx < 0 or idx >= len(self.server_list):
            return

        self.frames[idx].grid(row=0, column=2, rowspan=2, sticky=(N, S, W, E), padx=5, pady=10)
        # 刷新状态btn_refresh
        self.frames[idx].status_refresh()
        if self.last_select >= 0:
            self.frames[self.last_select].grid_forget()

        self.last_select = idx

    def __current_index(self) -> int:
        """
        当前选择的列表索引
        """
        indices = self.lbox.curselection()
        print('select:', indices)
        if len(indices) == 0:
            return -1
        if len(indices) != 1:
            raise RuntimeError('the listbox select not one! %s' % indices)
        return indices[0]

    def select_server(self, index):
        self.lbox.selection_clear(0, len(self.server_list))
        self.lbox.select_set(index)
        self.lbox.see(index)
        self.__listbox_select()

    def show_cmd_result(self, cmds):
        """
        显示命令结果
        """
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
                  CmdData('终端', 'mysql -uroot -p', CmdData.TYPE_OF_INTERACTIVE, ['password', '123456', '>'])]

    mysql_data = ServerData(title='mysql', status_cmd='ps -ef|grep mysql|grep -v grep', btn_list=mysql_list)

    redis_list = [CmdData('启动1', 'ls', CmdData.TYPE_OF_NORMAL),
                  CmdData('停止1', 'ls', CmdData.TYPE_OF_NORMAL),
                  CmdData('重启1', 'ls', CmdData.TYPE_OF_NORMAL),
                  CmdData('日志1', 'ls', CmdData.TYPE_OF_LOOP),
                  CmdData('终端1', 'ls', CmdData.TYPE_OF_INTERACTIVE)]

    redis_data = ServerData(title='redis', status_cmd='ps -ef|grep redis', btn_list=redis_list)

    mainui = MainUI(root, servers_data=[mysql_data, redis_data], padding=5)
    mainui.grid(row=0, column=0, sticky=(N, S, W, E))

    root.mainloop()

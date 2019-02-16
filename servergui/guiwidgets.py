"""
Create by wuxingle on 2018/12/3
服务管理界面
"""
from tkinter import font

import PIL.Image
from PIL import ImageTk

from servergui.basedata import *
from servergui.termwidgets import *

log = logger.get(__name__)


class BaseDialog(Toplevel):
    """
    基础对话框
    """

    def __init__(self, title, close_handle=None, **kw):
        super().__init__(**kw)
        self.title(title)
        self.close_handle = close_handle

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # 先隐藏
        self.withdraw()

    def show(self, x=None, y=None):
        """
        显示,默认x/2,y/4
        :param x: 屏幕位置x
        :param y: 屏幕位置y
        """
        self.update_idletasks()
        self.deiconify()
        self.withdraw()

        x = (self.winfo_screenwidth() - self.winfo_width()) // 2 if x is None else x
        y = (self.winfo_screenheight() - self.winfo_height()) // 4 if y is None else y
        self.geometry('%sx%s+%s+%s' % (self.winfo_width(), self.winfo_height(), x, y))

        self.deiconify()

    def destroy(self):
        if callable(self.close_handle):
            self.close_handle()
        super().destroy()


def show_edit_dialog(title: str, init_str: str, res_handle, x=None, y=None):
    """
    显示编辑对话框
    :param title: 标题
    :param init_str: 初始化数据
    :param res_handle: 数据处理
    :param x: 显示在屏幕的x位置
    :param y: 显示在屏幕的y位置
    """
    win = BaseDialog(title)

    fra = ttk.Frame(win, padding=10)

    txt = Text(fra, height=5, width=40)
    txt.insert(END, init_str)
    txt.focus_set()

    def ok(*args):
        res_handle(txt.get('1.0', END).rstrip())
        win.destroy()

    btn_ok = ttk.Button(fra, text='确定', command=ok, default='active')

    txt.grid(column=0, row=0, sticky=(N, S, W, E), pady=5)
    btn_ok.grid(column=0, row=1, pady=5)

    win.bind('<Return>', ok)
    fra.columnconfigure(0, weight=1)
    fra.rowconfigure(0, weight=1)
    fra.rowconfigure(1, weight=1)
    fra.grid(column=0, row=0, sticky=(N, S, W, E))

    win.show(x, y)


def show_cmd_modify_dialog(title, edit_handle, del_handle=None,
                           init_data: CmdData = CmdData('', '', CmdData.TYPE_OF_NORMAL, []),
                           x=None, y=None):
    """
    编辑命令对话框
    :param title: 标题
    :param edit_handle: 命令处理函数
    :param del_handle: 点击删除的处理函数
    :param init_data: 初始化数据
    :param x: 屏幕位置x
    :param y: 屏幕位置y
    """
    win = BaseDialog(title)
    fra = ttk.Frame(win, padding=10)

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

        real_exp = [e for e in exp if e and e.strip()]
        edit_handle(CmdData(name, c, tp, real_exp))
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
    fra.grid(column=0, row=0, sticky=(N, S, W, E))
    win.bind('<Return>', ok)

    win.show(x, y)


class ServerItemUI(ttk.Frame):
    """
    单个服务界面
    """

    def __init__(self, master, server_data: ServerData, active_img=None, dead_img=None, **kw):
        """
        :param server_data: 服务对象
        :param active_img: 运行中图
        :param dead_img: 停止图
        """
        super().__init__(master, **kw)
        self.server_data = server_data
        self.active_img = active_img
        self.dead_img = dead_img

        # 标题和刷新栏
        self.title_var = StringVar(value=server_data.title)
        lab_title = ttk.Label(self, textvariable=self.title_var, anchor=CENTER, font=font.Font(size=20))

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
        for btn_data in server_data.sub_cmds:
            btn = self.__create_btn(btn_data)
            btn.grid(row=i, column=0, columnspan=2, sticky=(N, S, W, E), padx=10, pady=5)
            i = i + 1

        # 动态添加按钮
        def add_cmd_btn(*args):
            def add_cmd(cmd_data: CmdData):
                if not cmd_data.name or not cmd_data.name.strip():
                    log.warning('add server, name can not empty:%s', cmd_data)
                    return
                server_data.sub_cmds.append(cmd_data)
                b = self.__create_btn(cmd_data)
                self.max_column = self.max_column + 1
                btn_add.grid(row=self.max_column + 1, column=0, columnspan=2, sticky=(W, E), padx=10, pady=5)
                b.grid(row=self.max_column, column=0, columnspan=2, sticky=(N, S, W, E), padx=10, pady=5)

            show_cmd_modify_dialog('添加', add_cmd)

        btn_add = ttk.Button(self, text='➕', command=add_cmd_btn)
        btn_add.grid(row=i, column=0, columnspan=2, sticky=(W, E), padx=10, pady=5)
        self.max_column = i
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
                if not new_data.name or not new_data.name.strip():
                    log.warning('edit server, name can not empty:%s', new_data)
                    return
                cmd_data.name = new_data.name
                cmd_data.tp = new_data.tp
                cmd_data.cmd = new_data.cmd
                cmd_data.expects = new_data.expects
                name_var.set(new_data.name)

            def del_btn():
                self.server_data.sub_cmds.remove(cmd_data)
                btn.grid_remove()

            show_cmd_modify_dialog('编辑', edit_handle, del_btn, cmd_data)

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
                log.error('the cmd data tp not allowed:%s', cmd_data)
                return

            term.grid(row=0, column=0, sticky=(N, S, W, E))
            term.start()

        return click

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
    """
    主界面
    """

    def __init__(self, master, servers_data, close_handle=None,
                 active_img_path=None, dead_img_path=None, **kw):
        super().__init__(master, **kw)

        self.servers_data = servers_data
        self.close_handle = close_handle
        self.active_img = ImageTk.PhotoImage(PIL.Image.open(active_img_path))
        self.dead_img = ImageTk.PhotoImage(PIL.Image.open(dead_img_path))

        # 左边界面
        btn_add = ttk.Button(self, text='➕', command=self.add_server)
        btn_sub = ttk.Button(self, text='➖', command=self.del_server)

        # 服务列表
        self.servers_name = list(map(lambda d: d.title, self.servers_data))
        self.lbox_var = StringVar(value=self.servers_name)
        self.lbox = Listbox(self, listvariable=self.lbox_var)
        self.lbox['relief'] = 'sunken'

        btn_add.grid(row=0, column=0, sticky=(N, W, E))
        btn_sub.grid(row=0, column=1, sticky=(N, W, E))
        self.lbox.grid(row=1, column=0, columnspan=2, sticky=(N, W, E, S), padx=5)
        self.lbox.bind('<<ListboxSelect>>', self.__select_listbox)
        self.lbox.bind('<Button-2>', self.edit_listbox)
        self.lbox.bind('<Double-1>', self.edit_listbox)

        # 初始化右边界面
        self.server_frames: List[ServerItemUI] = []
        for data in self.servers_data:
            fra = ServerItemUI(self, data, self.active_img, self.dead_img)
            self.server_frames.append(fra)

        self.last_select = -1
        self.select_server(0)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)

        self.lbox.select_set(0)

    def destroy(self):
        if callable(self.close_handle):
            self.close_handle()

        super().destroy()

    def __select_listbox(self, *args):
        """
        列表选择，切换右边的界面
        """
        idx = self.current_select()
        if idx == self.last_select or idx < 0 or idx >= len(self.servers_name):
            return

        self.server_frames[idx].grid(row=0, column=2, rowspan=2, sticky=(N, S, W, E), padx=5, pady=10)
        # 刷新状态btn_refresh
        self.server_frames[idx].status_refresh()
        if self.last_select >= 0:
            self.server_frames[self.last_select].grid_forget()

        self.last_select = idx

    def add_server(self, *args):

        def handle(s):
            if not s or not s.strip():
                return
            server_data = ServerData(s, '', [CmdData('请编辑', '', CmdData.TYPE_OF_NORMAL)])
            self.servers_data.append(server_data)
            self.servers_name.append(s)
            self.lbox_var.set(self.servers_name)

            fra = ServerItemUI(self, server_data, self.active_img, self.dead_img)
            fra.status_dead()
            self.server_frames.append(fra)
            self.select_server(len(self.servers_name) - 1)

        show_edit_dialog('请输入服务名', '', handle)

    def del_server(self, *args):
        index = self.current_select()
        if index < 0:
            return

        self.servers_data.pop(index)
        self.servers_name.pop(index)
        self.server_frames.pop(index).grid_remove()

        self.lbox_var.set(self.servers_name)

        if index >= len(self.servers_name):
            index = index - 1

        self.last_select = -1
        self.select_server(index)

    def edit_listbox(self, *args):
        """
        列表选项名字编辑
        """
        idx = self.current_select()
        if idx < 0 or idx >= len(self.servers_name):
            return

        def edit(s):
            self.servers_name[idx] = s
            self.lbox_var.set(self.servers_name)
            self.server_frames[idx].set_title(s)

        show_edit_dialog('编辑', self.servers_name[idx], edit)

    def current_select(self) -> int:
        """
        当前选择的列表索引
        """
        indices = self.lbox.curselection()
        if len(indices) == 0:
            return -1
        if len(indices) != 1:
            raise RuntimeError('the listbox select not one! %s' % indices)
        return indices[0]

    def select_server(self, index):
        """
        选择显示第几个服务
        """
        self.lbox.selection_clear(0, len(self.servers_name))
        self.lbox.select_set(index)
        self.lbox.see(index)
        self.__select_listbox()

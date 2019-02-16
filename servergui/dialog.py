"""
Create by wuxingle on 2019/1/6
自定义对话框,一次只弹出一个
"""

from tkinter import *
from tkinter import ttk

from servergui.basedata import *


class BaseDialog(Toplevel):
    """
    基础弹窗
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

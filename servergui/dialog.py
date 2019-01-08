"""
Create by wuxingle on 2019/1/6
自定义对话框
"""

from tkinter import *
from tkinter import ttk


class BaseDialog(Toplevel):
    def __init__(self, title, close_handle=None, **kw):
        super().__init__(**kw)
        self.title(title)
        self.close_handle = close_handle

        self.fra = ttk.Frame(self, padding=10)

        self.fra.grid(column=0, row=0, sticky=(N, S, W, E))
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def content(self) -> ttk.Frame:
        return self.fra

    def destroy(self):
        if callable(self.close_handle):
            self.close_handle()
        super().destroy()


def show_edit_dialog(title: str, init_str: str, res_handle):
    """
    显示编辑对话框
    :param title: 标题
    :param init_str: 初始化数据
    :param res_handle: 数据处理
    """
    win = BaseDialog(title)
    fra = win.content()

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

"""
Create by wuxingle on 2018/12/3
服务管理界面
"""

from tkinter import *
from tkinter import ttk

root = Tk()
root.title('服务管理')
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

content = ttk.Frame(root, padding=5)

# 左边列表
list_ser_var = StringVar(value=['mysql', 'redis'])
listbox_ser = Listbox(content, listvariable=list_ser_var)
listbox_ser['relief'] = 'sunken'

# 状态label
lab_status = ttk.Label(content, text='running\nrunning', anchor=CENTER)
lab_status['relief'] = 'sunken'

# button
btn_term = ttk.Button(content, text='终端')
btn_start = ttk.Button(content, text='启动')
btn_stop = ttk.Button(content, text='关闭')
btn_restart = ttk.Button(content, text='重启')
btn_log = ttk.Button(content, text='日志')

# 基本信息text
text_basic = Text(content, width=40, height=5, wrap='none')

content.rowconfigure(2, weight=1)
content.columnconfigure(0, weight=2)
content.columnconfigure(1, weight=1)
content.columnconfigure(2, weight=1)
content.columnconfigure(3, weight=1)
content.columnconfigure(4, weight=1)
content.columnconfigure(5, weight=1)
content.grid(row=0, column=0, sticky=(N, S, W, E))

listbox_ser.grid(row=0, column=0, rowspan=3, sticky=(N, S, W, E), padx=5, pady=10)
lab_status.grid(row=0, column=1, columnspan=5, sticky=(N, W, E), padx=5, pady=10)
btn_term.grid(row=1, column=1, sticky=(N, S), padx=10, pady=10)
btn_start.grid(row=1, column=2, sticky=(N, S), padx=10, pady=10)
btn_stop.grid(row=1, column=3, sticky=(N, S), padx=10, pady=10)
btn_restart.grid(row=1, column=4, sticky=(N, S), padx=10, pady=10)
btn_log.grid(row=1, column=5, sticky=(N, S), padx=10, pady=10)
text_basic.grid(row=2, column=1, columnspan=5, sticky=(N, S, W, E), padx=5, pady=10)

root.mainloop()

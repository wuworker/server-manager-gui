"""
Create by wuxingle on 2018/12/12
"""
from tkinter import *
from tkinter import ttk

from servergui import termwidgets

root = Tk()
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# term = termwidgets.InteractiveTerminalUI(
#     root, cmd_start=['mysql -uroot -p', 'password', '123456', 'mysql>'], expects='>', padding=10)

term = termwidgets.OnceTerminalUI(master=root, cmd='/Users/wxl/test.sh')
term.grid(row=0, column=0, sticky=(N, S, W, E))
term.start()

root.mainloop()

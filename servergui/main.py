"""
Create by wuxingle on 2019/2/16
"""
VERSION = 'v1.0'
LOG_CONFIG_FILE = './config/logging.yml'
IMG_STATUS_ACTIVE = "./img/status_active.gif"
IMG_STATUS_DEAD = "./img/status_dead.gif"
DATA_FILE = './data/servers.json'

from servergui import logger

logger.init_logging(LOG_CONFIG_FILE)

from servergui.guiwidgets import *
from tkinter import messagebox

datas = load_servers_data(DATA_FILE)

root = Tk()
# 隐藏窗口
root.withdraw()

root.title('服务管理' + VERSION)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)


def on_closing():
    save = messagebox.askquestion('关闭', '是否保存当前配置')
    if save == 'yes':
        save_servers_data(DATA_FILE, datas)


mainui = MainUI(root, datas, close_handle=on_closing,
                active_img_path=IMG_STATUS_ACTIVE, dead_img_path=IMG_STATUS_DEAD,
                padding=5)
mainui.grid(row=0, column=0, sticky=(N, S, W, E))

root.update_idletasks()
root.deiconify()
root.withdraw()
root.geometry('%sx%s+%s+%s' % (root.winfo_width(), root.winfo_height(), 200, 200))
root.deiconify()

root.mainloop()

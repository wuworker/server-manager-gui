"""
Create by wuxingle on 2019/2/16
基本数据对象
"""
import json
import os
from typing import List


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
        return json.dumps(self, ensure_ascii=False, default=lambda obj: obj.__dict__)

    __repr__ = __str__

    @staticmethod
    def from_dict(d):
        name = d['name']
        if not name or not name.strip():
            raise ValueError("CmdData json '%s' the name can not empty!" % (d,))
        cmd = d['cmd']
        if cmd and type(cmd) != str:
            raise TypeError("CmdData json '%s' the cmd must is str!" % (d,))
        tp = d['tp']
        if tp is None:
            raise ValueError("CmdData json '%s' the tp can not empty!" % (d,))
        tp = int(tp)
        if tp != CmdData.TYPE_OF_NORMAL and tp != CmdData.TYPE_OF_LOOP and tp != CmdData.TYPE_OF_INTERACTIVE:
            raise ValueError("CmdData json '%s' the tp must is [0/1/2]!" % (d,))

        exp = d['expects']
        if exp and type(exp) != list:
            raise TypeError("CmdData json '%s' the expects must is list!", d)
        if tp == CmdData.TYPE_OF_INTERACTIVE and len(exp) == 0:
            raise ValueError(
                "CmdData json '%s' the expects can not empty where tp is %s" % (d, CmdData.TYPE_OF_INTERACTIVE))

        return CmdData(name, cmd, tp, exp)


class ServerData:
    """
    服务对象
    """

    def __init__(self, title: str, status_cmd: str, sub_cmds: List[CmdData]):
        """
        :param title: 服务名称
        :param status_cmd: 判断状态的命令
        :param sub_cmds: 具体的子命令
        """
        self.title = title
        self.status_cmd = status_cmd
        self.sub_cmds = sub_cmds

    def __str__(self):
        return json.dumps(self, ensure_ascii=False, default=lambda obj: obj.__dict__)

    __repr__ = __str__

    @staticmethod
    def from_dict(d):
        title = d['title']
        if not title or not title.strip():
            raise ValueError("ServerData json '%s' the title can not empty!" % (d,))
        status_cmd = d['status_cmd']
        if status_cmd and type(status_cmd) != str:
            raise TypeError("ServerData json '%s' the status_cmd must is str!" % (d,))
        sub_cmds = d['sub_cmds']
        if sub_cmds and type(sub_cmds) != list:
            raise TypeError("ServerData json '%s' the sub_cmds must is list!", d)

        return ServerData(title, status_cmd, list(map(lambda c: CmdData.from_dict(c), sub_cmds)))


def save_servers_data(data_file, servers_data: List[ServerData]):
    """
    保存数据到文件
    :param data_file: 文件路径
    :param servers_data: 数据
    """
    with open(data_file, 'w') as f:
        json.dump(servers_data, f, default=lambda obj: obj.__dict__, ensure_ascii=False, indent=4)


def load_servers_data(data_file) -> List[ServerData]:
    """
    从文件读取数据
    :param data_file: 文件路径
    :return: 数据
    """
    servers_data = []
    if not os.path.isfile(data_file):
        raise RuntimeError("the file:'%s' not exists!" % (data_file,))
    with open(data_file, 'r') as f:
        l = json.load(f)
    for d in l:
        servers_data.append(ServerData.from_dict(d))
    return servers_data

"""
Create by wuxingle on 2018/12/8
日志
"""
import logging
import logging.config
import yaml

CONFIG_FILE = '../config/logging.yml'


def init_logging():
    with open(CONFIG_FILE, 'r') as conf:
        dist_conf = yaml.load(conf)
    logging.config.dictConfig(dist_conf)


print('------------init log---------------------')
init_logging()


def get(name=None):
    print('get logs name:', name)
    return logging.getLogger(name)

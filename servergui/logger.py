"""
Create by wuxingle on 2018/12/8
日志
"""
import logging
import logging.config

import yaml


def init_logging(config_file):
    with open(config_file, 'r') as conf:
        dist_conf = yaml.load(conf)
    logging.config.dictConfig(dist_conf)


def get(name=None):
    return logging.getLogger(name)

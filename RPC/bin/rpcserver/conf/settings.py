# -*- coding:utf-8 -*-
__author__ = 'shisanjun'

import os
import sys
import logging

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

#日志等级DEBUG，INFO，ERROR
LOG_LEVEL=logging.DEBUG
#日志文件
LOG_FILE="rpc.log"
#本机地址
LOCAL_HOST="192.168.6.22"
#RABBITMQ地址
RABBITMQ_HOST="192.168.6.23"
#RABBITMQ用户名
RABBITMQ_USER="shi"
#RABBITMQ密码
RABBITMQ_PASSWORD="123456"

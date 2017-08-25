# -*- coding:utf-8 -*-
__author__ = 'shisanjun'

import os,sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from src.rpc_server import RpcServer
from conf import settings

if __name__ == "__main__":
    #queue_name为本地ip地址
    queue_name =settings.LOCAL_HOST
    server = RpcServer(queue_name)
    server.start()
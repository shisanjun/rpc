# -*- coding:utf-8 -*-
__author__ = 'shisanjun'
import os,sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from src.rpc_client import RpcClinet
from conf import settings

if __name__ == "__main__":
     rpc=RpcClinet()
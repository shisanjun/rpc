# -*- coding:utf-8 -*-
__author__ = 'shisanjun'

import os,sys
import logging
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from conf import settings

def log_fun():

    log_dir=os.path.join(BASE_DIR,"log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file=os.path.join(log_dir,settings.LOG_FILE)
    log_level=settings.LOG_LEVEL

    log_obj=logging.getLogger(__file__)
    log_obj.setLevel(logging.DEBUG)

    shandler=logging.StreamHandler()
    shandler.setLevel(log_level)

    fhandler=logging.FileHandler(log_file,encoding="utf-8")
    fhandler.setLevel(log_level)

    fomatter=logging.Formatter('%(asctime)s  %(levelname)s - %(message)s')

    shandler.setFormatter(fomatter)
    fhandler.setFormatter(fomatter)

    if len(log_obj.handlers) >=1:
        return

    log_obj.addHandler(shandler)
    log_obj.addHandler(fhandler)
    return log_obj
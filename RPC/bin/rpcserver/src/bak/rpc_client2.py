# -*- coding:utf-8 -*-
__author__ = 'shisanjun'

import os,sys
import pika
import uuid
import threading
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.log import log_fun
from conf import settings


class RpcClinet(object):

    logger=log_fun()
    task_num=0
    task_dict={}
    def __init__(self):
        self.rabbitmq_host=settings.RABBITMQ_HOST
        self.rabbitmq_user=settings.RABBITMQ_USER
        self.rabbitmq_password=settings.RABBITMQ_PASSWORD

        self.credentials=pika.PlainCredentials(username=self.rabbitmq_user,password=self.rabbitmq_password)
        #获取连接
        self.connection=pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host,credentials=self.credentials))
        #实例通道
        self.channel=self.connection.channel()


        self.interactive()

    def format_str(self,s,type="green"):

        if type=="red":
            print("\033[1;31m%s\033[0m" %s)
        elif type=="green":
            print("\033[1;32m%s\033[0m" %s)
        else:
            print("\033[1;33m%s\033[0m" %s)

    def format_input(self,str1):
        """
        format input string
        """
        while True:
            str_tmp=input("%s>>" %str1).strip()
            if len(str_tmp)==0:continue
            else:break
        return str_tmp

    def interactive(self):
        print_cmd="""
        命令格式：
            run cmd --hosts ip1,ip2
            check_task list
            check_task taskid

            example:
            run "df -h" --hosts 192.168.1.1,192.168.1.2
            check_task 1
        """
        self.format_str(print_cmd)
        while True:
            cmd_str=self.format_input("请输入执行命令")
            if cmd_str=="exit":break

            cmd_dict=self.cmd_parse(cmd_str)
            if cmd_dict is  None:
                continue

            if hasattr(self,str(cmd_dict.get("action"))):
                getattr(self,str(cmd_dict.get("action")))(cmd_dict)

    def cmd_parse(self,cmd_str):
        cmd_dict={}
        if cmd_str.startswith("run"):
            if "--hosts" not in cmd_str:
                self.logger.error("没有参数--hosts")
                return
            cmd_list=cmd_str.split("--hosts")
            run_list=cmd_list[0].strip().split()

            #判读有没有输入执行命令
            if len(run_list)<2:
                self.logger.error("没有输入执行命令")
                return

            run_cmd=cmd_list[0].strip("run").strip()

            #获取主机，去除',"符号
            hosts=cmd_list[-1].strip().strip("'").strip('"').split(",")

            #判断有没有主机
            if len(hosts)==1 and hosts[0]=='':
                self.logger.error("没有输入执行主机")
                return

            cmd_dict["action"]="run"
            cmd_dict["cmd"]=run_cmd
            cmd_dict["hosts"]=hosts

        elif cmd_str.startswith("check_task"):
            cmd_list=cmd_str.split()
            if len(cmd_list)<2:
                self.logger.error("没有输入任务ID")
                return

            cmd_dict["action"]="check_task"
            cmd_dict["taskid"]=cmd_list[1]

        return cmd_dict

    def run(self,cmd_dict):
        hosts=cmd_dict.get("hosts")
        cmd_str=cmd_dict.get("cmd")

        for host in hosts:
            self.task_num+=1
            response=self.send_MQ(host,cmd_str)
            self.task_dict["%s"%self.task_num]=[host,cmd_str,response[0],response[1]]


    def send_MQ(self,host,run_cmd):

        self.channel.exchange_declare(exchange="cmd",exchange_type="direct",durable=True)
        result=self.channel.queue_declare(exclusive=False,durable=True)
        callback_queue=result.method.queue

        corr_id=str(uuid.uuid4())
        self.channel.basic_publish(
            exchange="cmd",
            routing_key=host,
            properties=pika.BasicProperties
            (
                reply_to=callback_queue,
                correlation_id=corr_id,
                delivery_mode=2
            ),
            body=run_cmd,
            )
        return callback_queue,corr_id

    def recv_MQ(self,callback_queue,corr_id):

        self.response=None
        self.corr_id=corr_id
        print("111111111")
        #接受消息准备
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.recv_reponse,queue=callback_queue,no_ack=True)

        while self.response is None:
            self.connection.process_data_events()

        return self.response


    def recv_reponse(self,ch,method,props,body):

        if self.corr_id==props.correlation_id:
            self.response=body.decode("utf-8","ignore")
            print(body.decode("utf-8","ignore"))
            self.channel.basic_ack(delivery_tag=method.delivery_tag)


    def check_task(self,task_dict):
        cmd_str=task_dict.get("taskid")
        print(cmd_str)
        if "list" in cmd_str:
            for task_tmp in  self.task_dict.keys():
                self.format_str("task[%s]"%task_tmp)
            self.format_str("查看命令结果：check_task 任务号")
        else:

            if cmd_str in self.task_dict:
                print(self.task_dict.get(cmd_str))
                print("111")
                host=self.task_dict.get(cmd_str)[0]
                cmd_tmp=self.task_dict.get(cmd_str)[1]
                callback_queue=self.task_dict.get(cmd_str)[2]
                corr_id=self.task_dict.get(cmd_str)[3]
                result=self.recv_MQ(callback_queue,corr_id)
                print(result.decode("utf-8"))

rpc=RpcClinet()
# -*- coding:utf-8 -*-
__author__ = 'shisanjun'

import os,sys
import pika
import uuid
import gevent
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.log import log_fun
from conf import settings


class RpcClinet(object):

    logger=log_fun()
    #任务编号
    task_num=0
    task_dict={}
    def __init__(self):
        #设置RabbitMQ的主机，用户名和密码
        self.rabbitmq_host=settings.RABBITMQ_HOST
        self.rabbitmq_user=settings.RABBITMQ_USER
        self.rabbitmq_password=settings.RABBITMQ_PASSWORD

        #设置rabbitmq认证
        self.credentials=pika.PlainCredentials(username=self.rabbitmq_user,password=self.rabbitmq_password)
        #获取连接
        self.connection=pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host,credentials=self.credentials))
        #实例通道
        self.channel=self.connection.channel()

        #交互接口
        self.interactive()

    def format_str(self,s,type="green"):
        """
        颜色显示
        """
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
        """
        交互方法
        :return:
        """
        self.logger.debug("begin rpc client..........")
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
        gevent_list=[]
        while True:
            cmd_str=self.format_input("请输入执行命令")
            self.logger.debug("rpc cmd:%s" %cmd_str)
            if cmd_str=="exit":
                #退出清空协程列表
                self.logger.debug("close rpc client..........")
                gevent_list=[]
                break

            cmd_dict=self.cmd_parse(cmd_str)
            if cmd_dict is  None:
                continue
            #增加协程
            gevent_list.append(gevent.spawn(self.response_action,cmd_dict))
            #调用协程
            gevent.joinall(gevent_list)

    def response_action(self,cmd_dict):
        if hasattr(self,str(cmd_dict.get("action"))):
            getattr(self,str(cmd_dict.get("action")))(cmd_dict)


    def cmd_parse(self,cmd_str):
        """
        格式化输入参数
        :param cmd_str:
        :return:
        """
        cmd_dict={}
        #判断是不是run 命令
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

        #判断是不是check_task命令
        elif cmd_str.startswith("check_task"):
            cmd_list=cmd_str.split()
            if len(cmd_list)<2:
                self.logger.error("没有输入任务ID")
                return

            cmd_dict["action"]="check_task"
            cmd_dict["taskid"]=cmd_list[1]

        return cmd_dict

    def run(self,cmd_dict):
        #执行run方法
        hosts=cmd_dict.get("hosts")
        cmd_str=cmd_dict.get("cmd")

        for host in hosts:
            #任务号
            self.task_num+=1
            response=self.call(host,cmd_str)
            self.task_dict["%s"%self.task_num]=[host,cmd_str,response[0],response[1]]

    def check_task(self,task_dict):
        #检查任务号
        cmd_str=task_dict.get("taskid")

        if "list" in cmd_str:
            for task_tmp in  self.task_dict.keys():
                self.format_str("task[%s]"%task_tmp)
            self.format_str("查看命令结果：check_task 任务号")
        else:

            if cmd_str in self.task_dict:


                # host=self.task_dict.get(cmd_str)[0]
                # cmd_tmp=self.task_dict.get(cmd_str)[1]
                callback_queue=self.task_dict.get(cmd_str)[2]
                corr_id=self.task_dict.get(cmd_str)[3]
                result=self.get_response(callback_queue,corr_id)
                print(result.decode("utf-8","ignore"))
                del self.task_dict[cmd_str]

    def on_response(self, ch, method, props, body):
        '''获取命令执行结果的回调函数'''
        # print("验证码核对",self.callback_id,props.correlation_id)
        if self.callback_id == props.correlation_id:  # 验证码核对
            self.response = body
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def get_response(self,callback_queue,callback_id):
        '''取队列里的值，获取callback_queued的执行结果'''
        self.callback_id = callback_id
        self.response = None
        self.channel.basic_consume(self.on_response,  # 只要收到消息就执行on_response
                                   queue=callback_queue)
        while self.response is None:
            self.connection.process_data_events()  # 非阻塞版的start_consuming
        return self.response

    def call(self,queue_name,command):
        '''队列里发送数据'''
        result = self.channel.queue_declare(exclusive=False) #exclusive=False
        self.callback_queue = result.method.queue
        self.corr_id = str(uuid.uuid4())
        # print(self.corr_id)
        self.channel.basic_publish(exchange='',
                                   routing_key=queue_name,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,  # 发送返回信息的队列name
                                       correlation_id=self.corr_id,  # 发送uuid 相当于验证码
                                   ),
                                   body=command)

        return self.callback_queue,self.corr_id

if __name__=="__main__":
    rpc=RpcClinet()
# -*- coding:utf-8 -*-
__author__ = 'shisanjun'

import subprocess
import os,sys
import pika
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.log import log_fun
from conf import settings

class RpcServer(object):
    logger=log_fun()
    def __init__(self,queue_name):
        #设置RabbitMQ的主机，用户名和密码
        self.rabbitmq_host=settings.RABBITMQ_HOST
        self.rabbitmq_user=settings.RABBITMQ_USER
        self.rabbitmq_password=settings.RABBITMQ_PASSWORD

        #设置rabbitmq认证
        self.credentials=pika.PlainCredentials(username=self.rabbitmq_user,password=self.rabbitmq_password)
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host,credentials=self.credentials))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)

    def cmd(self,cmd_str):

        """
        执行命令
        """
        cmd_str=cmd_str.decode("utf-8").strip("'").strip('"')

        result_tmp=subprocess.Popen(cmd_str,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output=result_tmp.stdout.read()
        erroutput=result_tmp.stderr.read()
        result=(output+erroutput).decode("utf-8","ignore")
        #print(result)
        if not result:
            result = "Wrong Command"
        return result

    def on_request(self,ch, method, props, body):
        response = self.cmd(body)
        self.logger.debug("recv cmd: %s" %response)
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,  # 回信息队列名
                         properties=pika.BasicProperties(correlation_id=
                                                         props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        self.logger.debug("send result to %s" %props.correlation_id)


    def start(self):
        self.logger.debug("begin wait rpc resquest.......")
        self.channel.basic_consume(self.on_request,
                                   queue=self.queue_name)

        print(" [x] Awaiting RPC requests")
        self.channel.start_consuming()


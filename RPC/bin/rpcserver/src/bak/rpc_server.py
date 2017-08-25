# -*- coding:utf-8 -*-
__author__ = 'shisanjun'

import subprocess
import pika

class RpcServer(object):
    #生成认证
    credentials=pika.PlainCredentials(username="shi",password="123456")
    #建立连接
    connection=pika.BlockingConnection(pika.ConnectionParameters(host="192.168.6.23",credentials=credentials))

    def __init__(self):
        #建立通道
        self.channel=self.connection.channel()
        self.mq_conn()
        self.mq_recive()

    def mq_conn(self):
        """
        exchange 与queue绑定
        """
        #申明exchange，类型为direct,并让exchange持久化
        #self.channel.exchange_declare(exchange="cmd",exchange_type="direct",durable=True)

        #建立queue，queue名随机分配，exclusive: Only allow access by the current connection自动将queue删除,并让队列持久化
        self.result=self.channel.queue_declare(exclusive=True,durable=True)
        #获取queue名称
        self.queue_name=self.result.method.queue
        #符合routing_key消息把exchange和queue绑定
        #self.channel.queue_bind(exchange="cmd",queue=self.queue_name,routing_key="192.168.6.23")

    def mq_recive(self):
        #设置权重prefetch_count=1表示在消息没有处理完，不接受消息
        self.channel.basic_qos(prefetch_count=1)
        #接受消息准备
        self.channel.basic_consume(self.request_call,queue=self.queue_name,no_ack=False)
        print("waiting RPC requests...........")
        #开始接受消息
        self.channel.start_consuming()


    def request_call(self,ch,method,props,body):
        """
        消息回调方法
        """

        #body是客户端发送过来的消息
        cmd_str=body

        #命令处理结果
        result_cmd=self.cmd(cmd_str.decode("utf-8"))


        #给客户端返回消息
        self.channel.basic_publish(
            exchange="",
            routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id,
                delivery_mode=2 #消息持久化
            ),
            body=result_cmd
        )
        #消息处理完删除queue中消息
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        print(result_cmd.decode("utf-8","ignore"))
        print(props.reply_to)

    def cmd(self,cmd_str):

        """
        执行命令
        """
        cmd_str=cmd_str.strip("'").strip('"')

        result=subprocess.Popen(cmd_str,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output=result.stdout.read()
        erroutput=result.stderr.read()
        return output+erroutput


if __name__=="__main__":
    server=RpcServer()

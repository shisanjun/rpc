#作业11

##本节作业

##作业：可以对指定机器异步的执行多个命令

###要求：
	可以对指定机器异步的执行多个命令
	例子：
	>>:run "df -h" --hosts 192.168.3.55 10.4.3.4   
	task id: 45334
	>>: check_task 45334
	>>:
	注意，每执行一条命令，即立刻生成一个任务ID,不需等待结果返回，通过命令check_task TASK_ID来得到任务结果


###博客地址:
	python网络编程--RabbitMQ http://www.cnblogs.com/lixiang1013/p/7182678.html
	缓存数据库介绍 http://www.cnblogs.com/lixiang1013/p/7255709.html
	缓存数据库-redis介绍 http://www.cnblogs.com/lixiang1013/p/7255721.html
	缓存数据库-redis安装和配置 http://www.cnblogs.com/lixiang1013/p/7255802.html
	缓存数据库-redis数据类型和操作（string) http://www.cnblogs.com/lixiang1013/p/7255921.html
	缓存数据库-redis数据类型和操作（hash) http://www.cnblogs.com/lixiang1013/p/7257348.html
	缓存数据库-redis数据类型和操作（list) http://www.cnblogs.com/lixiang1013/p/7258521.html
	缓存数据库-redis数据类型和操作（set) http://www.cnblogs.com/lixiang1013/p/7258588.html
	缓存数据库-redis数据类型和操作（sorted set)http://www.cnblogs.com/lixiang1013/p/7258610.html
	缓存数据库-redis(管道) http://www.cnblogs.com/lixiang1013/p/7265826.html
	缓存数据库-redis(订阅发布) http://www.cnblogs.com/lixiang1013/p/7290236.html



###程序结构
	├── rpcclient   				客户端程序目录
	│   ├── bin  					执行目录
	│   │   ├── __init__.py
	│   │   └── start.py
	│   ├── conf						配置目录
	│   │   ├── __init__.py
	│   │   └── settings.py			配置文件
	│   ├── __init__.py
	│   ├── log						日志目录
	│   │   ├── __init__.py
	│   │   └── rpc.log
	│   └── src						代码程序
	│       ├── __init__.py
	│       ├── log.py				日志程序
	│       └── rpc_client.py		客户端程序
	└── rpcserver					服务器端程序
	    ├── bin						执行目录
    │  	├── __init__.py
    │   └── start.py		
	    ├── conf					配置目录		
    │   ├── __init__.py
    │   └── settings.py				配置文件
    ├── __init__.py
    ├── log							日志目录
    │   ├── __init__.py
    │   └── rpc.log
    └── src							代码程序
        ├── __init__.py
        ├── log.py					日志程序
        └── rpc_server.py			服务端程序
    
###

####1. 程序说明
	
	可以对指定机器异步的执行多个命令
	例子：
	>>:run "df -h" --hosts 192.168.3.55 10.4.3.4   
	task id: 45334
	>>: check_task 45334
	>>:
	注意，每执行一条命令，即立刻生成一个任务ID,不需等待结果返回，通过命令check_task TASK_ID来得到任务结果

####2. 测试用例
		用例1：run "dir" --hosts 192.168.6.22：
        用例2：run "ipconfig" --hosts 192.168.6.22

####3. 程序测试

        1)python DAY11-李祥-RPC/bin/rpcclient/bin/start.py
        2)python DAY11-李祥-RPC/bin/rpcserver/bin/start.py

####4. 测试

#####	1）客户端
	
        命令格式：
            run cmd --hosts ip1,ip2
            check_task list
            check_task taskid

            example:
            run "df -h" --hosts 192.168.1.1,192.168.1.2
            check_task 1
        
	请输入执行命令>>run "dir" --hosts 192.168.6.22
	请输入执行命令>>run "ipconfig" --hosts 192.168.6.22
	请输入执行命令>>check_task list
	task[1]
	task[2]
	查看命令结果：check_task 任务号
	请输入执行命令>>check_task 1
 	 E еľ DATA
	 к EC10-1C79

 	E:\pythonѵҵ\DAY11--RPC\bin\rpcserver\bin Ŀ¼

	2017/08/21  20:51    <DIR>          .
	2017/08/21  20:51    <DIR>          ..
	2017/08/21  20:51               384 start.py
	2017/07/31  09:26                50 __init__.py
               2 ļ            434 ֽ
               2 Ŀ¼ 25,349,361,664 ֽ

	请输入执行命令>>check_task list
	task[2]
	查看命令结果：check_task 任务号
	请输入执行命令>>

---

#####	2）服务端
	2017-08-22 11:02:19,332  DEBUG - begin wait rpc resquest.......
	2017-08-22 11:02:33,674  DEBUG - recv cmd:   E еľ DATA
	2017-08-22 11:02:33,674  DEBUG - send result to 7a3cccb1-f8aa-48c4-b7b0-d307df4c2058
	2017-08-22 11:02:45,805  DEBUG - recv cmd: 
	2017-08-22 11:02:45,806  DEBUG - send result to f5ec2a81-8844-4a18-aeb5-6a59f3beb13a

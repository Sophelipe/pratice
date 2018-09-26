# -*- coding: utf-8 -*-
# rpcserver.py

import pika

class RPCServer(object):
    def __init__(self, handler):
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue='rpc_queue')
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(handler.on_request, queue='rpc_queue')

    def start(self):
        self._channel.start_consuming()

if __name__ == '__main__':

    # 写几个测试方法

    def add(x, y):
        return x+y

    def printdict(**kwargs):
        cnt = 0
        for k, v in kwargs.iteritems():
            print(''.join(['"', str(k), '":"', str(v), '"']))
            cnt += 1
        return cnt

    def score(name="None", score = 100):
        print("Hello, %s. Your socore is %d " % (name, score))

    # 新建一个handler类实例, 并将add, printdict方法注册到handler里面
    from rpchandler import RPCHandler
    rpc_handler = RPCHandler()
    rpc_handler.register_function(add)
    rpc_handler.register_function(printdict)
    rpc_handler.register_function(score)

    # 运行server
    rpc_server = RPCServer(rpc_handler)

    print(" [x] Awaiting RPC requests")
    rpc_server.start()
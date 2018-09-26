# -*- coding: utf-8 -*-
import pika
import pickle
import uuid

class RPCClient(object):

    def __init__(self):

        self._connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost', port=5672))
        self._channel = self._connection.channel()

        result = self._channel.queue_declare(exclusive=True)
        self._callback_queue = result.method.queue

        self._channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self._callback_queue)

    def on_response(self, ch, method, props, body):

        if self._corr_id == props.correlation_id:
            self._response = body

    def __getattr__(self, name):
        # 通过name，得到一个函数
        def do_rpc(*args, **kwargs):
            self._response = None
            self._corr_id = str(uuid.uuid4())

            self._channel.basic_publish(
                exchange='',
                routing_key='rpc_queue',
                properties=pika.BasicProperties(
                    reply_to = self._callback_queue,
                    correlation_id = self._corr_id),
                body=pickle.dumps((name, args, kwargs)))
            while self._response is None:
                self._connection.process_data_events()
            result = pickle.loads(self._response)
            if isinstance(result, Exception):
                raise result
            return result

        return do_rpc

# 远程连接并且调用
if __name__ == '__main__':
    client = RPCClient()
    for i in range (100):

        print client.add(2,3)
        print client.printdict(**{"tab_space":"rpc", "github":"https://github.com/csdz"})
        client.score(name = 'Jhone', score = 100)


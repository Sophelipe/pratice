# -*- coding: utf-8 -*-
# rpchandler.py

import pika
import pickle

class RPCHandler(object):
    def __init__(self):
        # rpc functions map
        self._functions = {}

    def register_function(self, func):
        print("regist fucntion: %s" % func.__name__)
        self._functions[func.__name__] = func

    def on_request(self, ch, method, props, body):
        try:
            func_name, args, kwargs = pickle.loads(body)
            response = self._functions[func_name](*args, **kwargs)
            response = pickle.dumps(response)
        except Exception as e:
                response = pickle.dumps(e)
        finally:
            ch.basic_publish(exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(correlation_id = \
                                             props.correlation_id),
                body=response)

            ch.basic_ack(delivery_tag = method.delivery_tag)
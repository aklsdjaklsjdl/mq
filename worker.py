#!/usr/bin/env python
import pika
import time
import random
import urllib.parse
import sys
import time
import datetime
from booru import Booru
from rule34xxx import Rule34xxx
from gelbooru import Gelbooru
from atf import Atf
from paheal import Paheal
from e621 import E621
from time import sleep

def get_ids(url):
    parsed_url = urllib.parse.urlparse(url)
    if not parsed_url.scheme:
        print("not valid url ", url)
        return ("rule34xxx", set())
    print(parsed_url.netloc)
    images = set()
    if parsed_url.netloc == "rule34.xxx":
        images = Rule34xxx.get_page(url)
        return ("rule34xxx", images)
    elif parsed_url.netloc == "gelbooru.com":
        images = Gelbooru.get_page(url)
        return ("gelbooru", images)
    elif parsed_url.netloc == "booru.allthefallen.moe":
        images = Atf.get_page(url)
        return ("atf", images)
    elif parsed_url.netloc == "rule34.paheal.net":
        images = Paheal.get_page(url)
        return ("paheal", images)
    elif parsed_url.netloc == "e621.net":
        images = E621.get_page(url)
        return ("e621", images)

def get_all_urls(site, tag_list):
    if site == "rule34xxx":
        return Rule34xxx.get_all_urls(tag_list)
    elif site == "gelbooru" or site == 'gelbooru.com':
        return Gelbooru.get_all_urls(tag_list)
    #elif parsed_url.netloc == "booru.allthefallen.moe":
        #images = Atf.get_page(url)
        #return ("atf", images)
    #elif parsed_url.netloc == "rule34.paheal.net":
        #images = Paheal.get_page(url)
        #return ("paheal", images)
    #elif parsed_url.netloc == "e621.net":
        #images = E621.get_page(url)
        #return ("e621", images)
    raise Exception("only rule34xxx and gelbooru implemented")

class Queue:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost',heartbeat=600,
                                                       blocked_connection_timeout=300))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='booru', durable=True, arguments={"x-max-priority": 255})
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='booru', on_message_callback=self.callback)

    def start(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def handle(self, booru, id_):
        print(booru, id_)
        if id_ == 'v':
            print("FOUND V")
            return
        if id_.isdigit():
            Booru.post(booru, id_)
        else:
            print("Attempting taglist ", booru, id_)
            urls = get_all_urls(booru, id_.split(','))
            for url in urls:
                self.send("{}".format(url))

    def handle_url(self, url):
        if url.startswith("https://rule34.xxx/index.php?page=post&s=list&tags=V"):
            print("found V fuck fuck fuck")
            return
        (booru, images) = get_ids(url)
        for id_ in images:
            self.send("{} {}".format(booru, id_))

    def send(self, msg):
        random_number = random.randint(1, 80)
        self.channel.basic_publish(
            exchange='',
            routing_key='booru',
            body=msg,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                priority=random_number
            ))
        print(" [xx] Sent %r" % msg)

    def callback(self, ch, method, properties, body):
        msg = body.decode()
        print(" [x] Received %r, priority %d" % (msg, int(properties.priority)))
        args = msg.split(" ")
        if len(args) == 1:
            url = args[0]
            self.handle_url(url)
        elif len(args) == 2:
            try:
                self.handle(*args)
            except Exception as e:
                print("Exception", e)
                if int(properties.priority) == 255:
                    print("Max priority, not retrying message")
                    print(" [x] Done")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                timestamp = time.time()
                now = datetime.datetime.now()
                expire = 1000 * int((now.replace(hour=23, minute=59, second=59, microsecond=999999) - now).total_seconds())

		# to reject job we create new one with other priority and expiration
                self.channel.basic_publish(
                        exchange='', 
                        routing_key='booru', body=msg,
			properties=pika.BasicProperties(
                                delivery_mode=2, 
                                priority=int(properties.priority) + 1,
                                expiration='60000', 
                                headers=properties.headers
                        ))
                print("sending new msg with", int(timestamp), str(expire))
		# also do not forget to send back acknowledge about job
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print("[!] Rejected, going to sleep for a while")
                time.sleep(2)
                return
                # retry
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == '__main__':
    try:
        q = Queue()
        q.start()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

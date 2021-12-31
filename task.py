#!/usr/bin/env python
import pika
import sys
import random
from gelbooru import Gelbooru
from booru import Booru

def main(): 
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost',heartbeat=600,
                                               blocked_connection_timeout=300))
    channel = connection.channel()

    channel.queue_declare(queue='booru', durable=True, arguments={"x-max-priority": 255})
    args = sys.argv[1:]
    message = ' '.join(args) or None
    if message is None or len(args) > 2:
        return
    random_number = random.randint(1, 100)
    channel.basic_publish(
        exchange='',
        routing_key='booru',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            priority=random_number
        ))
    print(" [x] Sent %r" % message)

    connection.close()


if __name__ == "__main__":
    main()
    #for id_ in [6697603, 6394632]:
    #    Booru.post_image(Gelbooru.get_post(id_), "gelbooru", id_, False, False)

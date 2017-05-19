#!/usr/bin/env python
import pika
import sys


def ingest_files(queue, refdes, method, deployment, filenames):

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    for filename in filenames:
        headers = {'sensor': refdes, 'deliveryType': method, 'deploymentNumber': deployment}
        props = pika.BasicProperties(headers=headers, user_id='guest')

        channel.basic_publish(exchange='',
                              routing_key=queue,
                              body=filename,
                              properties=props)
        print(" [x] Sent %r" % filename)

    connection.close()


if __name__ == '__main__':

    queue = sys.argv[1]
    refdes = sys.argv[2]
    method = sys.argv[3]
    deployment = int(sys.argv[4])
    filenames = sys.argv[5:]

    ingest_files(queue, refdes, method, deployment, filenames)

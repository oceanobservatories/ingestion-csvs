#!/usr/bin/env python
"""
Usage:
    ingest_file.py <queue> <refdes> <method> <deployment> <filenames>

"""

import pika
import docopt

options = docopt.docopt(__doc__)


def ingest_files(_queue, _refdes, _method, _deployment, _filenames):

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    for filename in _filenames:
        headers = {'sensor': _refdes, 'deliveryType': _method, 'deploymentNumber': _deployment}
        props = pika.BasicProperties(headers=headers, user_id='guest')

        channel.basic_publish(exchange='',
                              routing_key=_queue,
                              body=filename,
                              properties=props)
        print(" [x] Sent %r" % filename)

    connection.close()


if __name__ == '__main__':
    # Get the command line options
    queue = options['<queue>']
    refdes = options['<refdes>']
    method = options['<method>']
    deployment = int(options['<deployment>'])
    filenames = options['<filenames>'].split(',')

    ingest_files(queue, refdes, method, deployment, filenames)

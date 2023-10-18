import os
import pika


def sent_message_into_queue(message: str) -> None:
    QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "")
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv("RABBITMQ_HOST", "")))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_publish(exchange='',
                          routing_key=QUEUE_NAME,
                          body=message)
    connection.close()

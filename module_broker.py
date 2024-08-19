import pika
import os
from dotenv import load_dotenv


def publish_message(queue_name, message):
    #  Load environment variables from .env file
    broker_host = os.getenv('MESSAGE_BROKER_HOST')
    broker_login = os.getenv('MESSAGE_BROKER_LOGIN')
    broker_password = os.getenv('MESSAGE_BROKER_PASSWORD')
    credentials = pika.PlainCredentials(broker_login, broker_password)

    # Establishing a connection to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=broker_host, port=5672, virtual_host='/', credentials=credentials)
    )
    channel = connection.channel()

    # Create a queue if it doesn't exist
    channel.queue_declare(queue=queue_name, durable=True)

    # Sending a message to the queue
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # The message will be saved to disk.
        )
    )

    connection.close()

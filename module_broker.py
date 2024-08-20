import pika
import os
from dotenv import load_dotenv


def connect_to_broker(queue_name):
    #  Load environment variables from .env file
    broker_host = os.getenv('MESSAGE_BROKER_HOST')
    # broker_host = 'localhost'
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

    return channel, connection


def publish_message(queue_name, message):
    channel, connection = connect_to_broker(queue_name)

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


def receive_message(queue_name):
    channel, connection = connect_to_broker(queue_name)

    # Set up a callback function to handle messages
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True  # Automatic confirmation of receipt of messages
    )
    channel.start_consuming()


def callback(ch, method, properties, body):
    print(f"Received: {body.decode()}")
    
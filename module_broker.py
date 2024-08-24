import pika
import os
from dotenv import load_dotenv


class BrokerClient:
    def __init__(self, queue_name):
        self.__queue_name = queue_name
        #  Load environment variables from .env file
        self.__broker_host = os.getenv('MESSAGE_BROKER_HOST', '127.0.0.1')
        __broker_login = os.getenv('MESSAGE_BROKER_LOGIN')
        __broker_password = os.getenv('MESSAGE_BROKER_PASSWORD')
        self.__credentials = pika.PlainCredentials(__broker_login, __broker_password)

    def __connect_to_broker(self):
        # Establishing a connection to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.__broker_host,
                                      port=5672,
                                      virtual_host='/',
                                      credentials=self.__credentials)
        )

        channel = connection.channel()

        # Create a queue if it doesn't exist
        channel.queue_declare(queue=self.__queue_name, durable=True)

        return channel, connection

    def publish_message(self, message):
        channel, connection = self.__connect_to_broker()

        # Sending a message to the queue
        channel.basic_publish(
            exchange='',
            routing_key=self.__queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # The message will be saved to disk.
            )
        )

        connection.close()

    # def receive_message(self):
    #     channel, connection = self.__connect_to_broker()
    #
    #     # Set up a callback function to handle messages
    #     channel.basic_consume(
    #         queue=self.__queue_name,
    #         on_message_callback=self.__callback,
    #         auto_ack=True  # Automatic confirmation of receipt of messages
    #     )
    #     channel.start_consuming()
    #
    # def __callback(self, ch, method, properties, body):
    #     print(f"Received: {body.decode()}")

import pika


def publish_message(queue_name, message, login, password):
    credentials = pika.PlainCredentials(login, password)

    # Establishing a connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', credentials))
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
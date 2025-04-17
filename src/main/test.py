from Infrastructure import messageQueue



if __name__ == "__main__":
    MQueue = messageQueue.MessageQueue(queue_name='test_queue')
    MQueue.connect()

    # Initialize the producer with the queue name
    producer = messageQueue.Producer('test_queue')

    # Send a message
    producer.send_message("Hello, RabbitMQ!")

    # Close the connection after sending the message
    producer.close()

    # External storage to hold the received messages
    external_storage = []

    # Initialize the consumer with the queue name and external storage
    consumer = messageQueue.Consumer('test_queue', external_storage=external_storage)

    # Start consuming messages
    consumer.consume_messages()

    print(consumer.external_storage[0])

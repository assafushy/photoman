import pika

credentials = pika.PlainCredentials('user', 'pass')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',30004,credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='hello')
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")
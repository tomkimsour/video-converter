import ffmpeg
import sys
import pika, os
import time

def main():
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['PRODUCTION_RABBITMQCLUSTER_SERVICE_HOST'], credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    def callback(ch, method, properties, body):
        # TODO: some converting in here
        print(" [x] Received %r" % body)
        time.sleep(3) #simulate 3 seconds job
        print(" [x] Done")
        ch.basic_ack(delivery_tag = method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def convert(in_filename:str, out_filename:str):
    try:
        stream = ffmpeg.input(in_filename)
        stream = ffmpeg.hflip(stream)
        stream = ffmpeg.output(stream, "output/"+out_filename)
        ffmpeg.run(stream)
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    convert('test.webm', 'testout.webm')

    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
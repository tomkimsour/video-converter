import ffmpeg
import sys
import pika, os
import time
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='august-tesla-333012-9c128488d3c3.json'

def main():
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['PRODUCTION_RABBITMQCLUSTER_SERVICE_HOST'], credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    def callback(ch, method, properties, body):
        body = body.decode('utf-8')
        print("Downloading blob")
        download_blob("video-bucket-storage", body, body)
        print("Downloaded blob, starting conversion")
        convert(body, body + "_converted")
        print("Conversion finished, uploading converted file")
        upload_blob("video-bucket-storage", body + "_converted.webm", body + "_converted")

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
        stream = ffmpeg.output(stream, out_filename + ".webm") # NOTE: THIS IS HARD CODED
        ffmpeg.run(stream)
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

def download_blob(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

if __name__ == '__main__':
    # convert('test.webm', 'testout.webm')

    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
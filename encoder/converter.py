import ffmpeg
import sys
import pika, os
import datetime
import requests
import threading
import functools
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='august-tesla-333012-9c128488d3c3.json'

def main():
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['PRODUCTION_RABBITMQCLUSTER_SERVICE_HOST'], credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    def callback(ch, method, properties, body, args):
        body = body.decode('utf-8')
        bucket_name = "video-bucket-storage"
        url = 'http://35.228.143.25:5000/status'
        conn = args
        delivery_tag = method.delivery_tag
        t1 = threading.Thread(target=convert_worker, args=(conn, ch, delivery_tag, body, "converted_" + body, url, bucket_name, body))
        t1.start()

    on_callback = functools.partial(callback, args=(connection))

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=on_callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def convert_worker(conn, ch, delivery_tag, in_filename:str, out_filename:str, url, bucket_name, body):
    requests.post(url, data = {"status": "Downloading from GCS", "status_id": 1, "id": body})
    download_blob(bucket_name, body, body)

    requests.post(url, data = {"status": "Converting", "status_id": 2, "id": body})
    out_filename = convert(body, "converted_" + body)

    requests.post(url, data = {"status": "Uploading converted video", "status_id": 3, "id": body})
    upload_blob(bucket_name, out_filename, out_filename)

    requests.post(url, data = {"status": "Generating URL", "status_id": 4, "id": body})
    signed_url = generate_download_signed_url_v4(bucket_name, out_filename)

    requests.post(url, data = {"status": signed_url, "status_id": 5, "id": body})

    cb = functools.partial(ack_message, ch, delivery_tag)
    conn.add_callback_threadsafe(cb)

def convert(in_filename:str, out_filename:str):
    out_filename = "converted_" + out_filename + ".mkv"
    
    try:
        stream = ffmpeg.input(in_filename)
        stream = ffmpeg.output(stream, out_filename)
        ffmpeg.run(stream)

        return out_filename
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

def generate_download_signed_url_v4(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=15),
        # Allow GET requests using this URL.
        method="GET",
    )

    return url

def ack_message(ch, delivery_tag):
    """Note that `ch` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).
    """
    if ch.is_open:
        ch.basic_ack(delivery_tag)
    else:
        # Channel is already closed, so we can't ACK this message;
        # log and/or do something that makes sense for your app in this case.
        pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
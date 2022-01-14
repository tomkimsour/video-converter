import ffmpeg
import sys
import pika, os, signal, time
import datetime
import requests
import threading
import functools
import json
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='august-tesla-333012-9c128488d3c3.json'

def callback(ch, method, properties, body, args):
    data = json.loads(body)
    bucket_name = "video-bucket-storage"
    url = 'http://flask-api-service.default.svc.cluster.local:5000/status'
    conn = args
    file_id = data['id']
    file_ext = data['ext']
    formatTo = data['formatTo']

    delivery_tag = method.delivery_tag
    t1 = threading.Thread(target=convert_worker, args=(conn, ch, delivery_tag, file_id, file_ext, formatTo, url, bucket_name))
    t1.start()

def main():
    #while(True):
        #try:
    credentials = pika.PlainCredentials('guest', 'guest')
    rabbit_mq_url = 'production-rabbitmqcluster.default.svc.cluster.local'
    # global connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_mq_url, credentials=credentials))
    # global channel
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)
    
    on_callback = functools.partial(callback, args=(connection))

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=on_callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
        # except pika.exceptions.ConnectionClosedByBroker:
        #     # Uncomment this to make the example not attempt recovery
        #     # from server-initiated connection closure, including
        #     # when the node is stopped cleanly
        #     #
        #     # break
        #     time.sleep(2)
        #     continue
        # # Do not recover on channel errors
        # except pika.exceptions.AMQPChannelError as err:
        #     print("Caught a channel error: {}, stopping...".format(err))
        #     time.sleep(2)
        #     continue
        # # Recover on all other connection errors
        # except pika.exceptions.AMQPConnectionError:
        #     print("Connection was closed, retrying...")
        #     time.sleep(2)
        #     continue


def convert_worker(conn, ch, delivery_tag, file_id, file_ext, formatTo, url, bucket_name):
    try:
        # if (os.path.isfile(file_id+file_ext)):
        #     # File exists: other thread is currently working on it
        #     return

        print("Posting status 1")
        requests.post(url, data = {"status": "Downloading from GCS", "status_id": 1, "id": file_id})
        download_blob(bucket_name, file_id+file_ext, file_id+file_ext)
        
        print("Posting status 2")
        requests.post(url, data = {"status": "Converting", "status_id": 2, "id": file_id})
        out_filename = convert(file_id+file_ext, file_id + formatTo)

        print("Posting status 3")
        requests.post(url, data = {"status": "Uploading converted video", "status_id": 3, "id": file_id})
        upload_blob(bucket_name, out_filename, out_filename)

        print("Posting status 4")
        requests.post(url, data = {"status": "Generating URL", "status_id": 4, "id": file_id})
        signed_url = generate_download_signed_url_v4(bucket_name, out_filename)
        
        print("Posting status 5")
        requests.post(url, data = {"status": signed_url, "status_id": 5, "id": file_id})

        cb = functools.partial(ack_message, ch, delivery_tag)
        conn.add_callback_threadsafe(cb)
        # cb = functools.partial(ack_message, delivery_tag)

        # while (True):
        #     try:
        #         print("Trying to ack")
        #         if (connection.add_callback_threadsafe(cb)):
        #             break
        #     except Exception as e:
        #         print(e)
        #     time.sleep(2)

    except Exception as e:
        # return
        print(e)
        os.kill(os.getpid(), signal.SIGINT)

def convert(in_filename:str, out_filename:str):
    out_filename = "converted_" + out_filename
    
    try:
        stream = ffmpeg.input(in_filename)
        stream = ffmpeg.output(stream, out_filename)
        ffmpeg.run(ffmpeg.overwrite_output(stream))

        return out_filename
    except ffmpeg.Error as e:
        print("ffmpeg error: " + e.stderr, file=sys.stderr)
        os.kill(os.getpid(), signal.SIGINT)
        # stream = ffmpeg.input(in_filename)
        # stream = ffmpeg.output(stream, out_filename)
        # ffmpeg.run(ffmpeg.overwrite_output(stream))
        # return out_filename

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
    print("trying to ack..")
    if ch.is_open:
        ch.basic_ack(delivery_tag)
        return True
    else:
        return False

if __name__ == '__main__':
    # try:
    main()
    # except KeyboardInterrupt as e:
    #     print('Interrupted: ')
    #     print(e)
    #     try:
    #         sys.exit(0)
    #     except SystemExit:
    #         os._exit(0)
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask_cors import CORS, cross_origin
import os
import uuid
import requests
from werkzeug.utils import secure_filename
from google.cloud import storage
import pika
import json
import time

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# max file upload value set to 500 mB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 500
# allowed extensions
app.config['UPLOAD_EXTENSIONS'] = ['.mp4', '.mkv', '.mov','.webm','.wmv','.avi','.avchd']
# path to the writting folder
app.config['UPLOAD_PATH'] = 'output'
api = Api(app)

# rabbitMQ setup
credentials = pika.PlainCredentials('guest', 'guest')

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='august-tesla-333012-9c128488d3c3.json'

clients = {}

metrics = {
    "times": [],
    "moving_average_last5": [],
    "queue_size": []
}

def upload_blob(blob_name, file_path, bucket_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        return True
    except Exception as e:
        print(e)
        return False

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"
    try:
        storage_client = storage.Client()

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()
    except Exception as e:
        print(e)
        return False

def createQueueTask(message):
    while(True):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['PRODUCTION_RABBITMQCLUSTER_SERVICE_HOST'], credentials=credentials))
            channel = connection.channel()
            channel.queue_declare(queue='task_queue', durable=True)
            channel.basic_publish(exchange='',
                                routing_key='task_queue',
                                body=message,
                                properties=pika.BasicProperties(
                                    delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE
                                ))
            connection.close()
            break
        except Exception as e:
            print(e)
            print("Failed to connect to RabbitMQ, trying again...")
            time.sleep(1)
            continue

class HomePage(Resource):
    def get(self):
        return {"text": "welcome"},200
    
class VideoConverter(Resource):
    def post(self):
        for uploaded_file in request.files.getlist('file'):
            if uploaded_file.filename != '':
                # sanitize file name
                filename = secure_filename(uploaded_file.filename)
                file_ext = os.path.splitext(filename)[1]

                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    return {"message": "file extension not in app config"},400

                if request.form['formatTo'] not in app.config['UPLOAD_EXTENSIONS']:
                    return {"message": "requested format not allowed"},400

                # writes the file in a bucket
                file_id = str(uuid.uuid4())
                bucket_name = "video-bucket-storage"
                
                #creates the file locally
                path = os.path.join(app.config['UPLOAD_PATH'], file_id)
                uploaded_file.save(path)
                
                if upload_blob(file_id + file_ext,path,bucket_name):
                    clients[file_id] = {
                        "status": "Uploaded",
                        "status_id": 0,
                        "status_url": f"http://34.88.103.252:5000/status/{file_id}",
                        "created": str(datetime.now()),
                        "elapsed_time": 0,
                        "ext": file_ext
                    }

                    # Update queue size metric
                    size = 0
                    for _,value in clients.items():
                        if (value['status_id'] != "5"):
                            size+=1
                    metrics['queue_size'].append(size)

                    data = {
                        "id": file_id,
                        "ext": file_ext,
                        "formatTo": request.form['formatTo']
                    }

                    msg = json.dumps(data)

                    createQueueTask(msg)
                    # if (not createQueueTask(msg)):
                    #     return {"Could not contact message queue"},400
                        
                    os.remove(path)
                    return clients[file_id],201
                return {"message": "could not upload to GCS"},400
            else:
                return {"message": "invalid file name"},400

class SetStatus(Resource):
    def post(self):
        clients[request.form['id']]['status'] = request.form['status']
        clients[request.form['id']]['status_id'] = request.form['status_id']

        if (clients[request.form['id']]['status_id'] == "2"):
            clients[request.form['id']]['conversion_started'] = str(datetime.now())

        if (clients[request.form['id']]['status_id'] == "3"):
            clients[request.form['id']]['conversion_time'] = (datetime.now() - datetime.fromisoformat(clients[request.form['id']]['conversion_started'])).total_seconds()

        if (clients[request.form['id']]['status_id'] == "5"): # finished stage
            clients[request.form['id']]['elapsed_time'] = (datetime.now() - datetime.fromisoformat(clients[request.form['id']]['created'])).total_seconds()
            metrics['times'].append(clients[request.form['id']]['elapsed_time'])

            if (len(metrics['times']) == 0):
                nr_values = 1
            elif (len(metrics['times']) >= 5):
                nr_values = 5
            else:
                nr_values = len(metrics['times'])

            metrics['moving_average_last5'].append(sum(metrics['times'][-5:]) / nr_values)
            #delete_blob("video-bucket-storage", request.form['id'] + clients[request.form['id']]['ext'])

class GetStatus(Resource):
    def get(self, id):
        return clients[id]

class Clients(Resource):
    def get(self):
        return clients

class Metrics(Resource):
    def get(self):
        return metrics

class Clear(Resource):
    def get(self):
        metrics['times'] = []
        metrics['moving_average_last5'] = []
        metrics['queue_size'] = []
        clients.clear()

api.add_resource(SetStatus, '/status')
api.add_resource(GetStatus, '/status/<id>')
api.add_resource(VideoConverter, '/upload')
api.add_resource(HomePage, '/')
api.add_resource(Clients, '/clients')
api.add_resource(Metrics, '/metrics')
api.add_resource(Clear, '/clear')

if __name__ == '__main__':
    app.run(debug=True)

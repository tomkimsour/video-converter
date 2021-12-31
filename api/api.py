from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask_cors import CORS, cross_origin
import os
import uuid
from werkzeug.utils import secure_filename
from google.cloud import storage
# import pika

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
# credentials = pika.PlainCredentials('guest', 'guest')
# connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['PRODUCTION_RABBITMQCLUSTER_SERVICE_HOST'], credentials=credentials))
# channel = connection.channel()
# channel.queue_declare(queue='task_queue', durable=True)
# connection.close()

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='august-tesla-333012-9c128488d3c3.json'


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

def createQueueTask(file_id):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['PRODUCTION_RABBITMQCLUSTER_SERVICE_HOST'], credentials=credentials))
        channel = connection.channel()

        channel.basic_publish(exchange='',
                            routing_key='task_queue',
                            body=file_id,
                            properties=pika.BasicProperties(
                                delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE
                            ))
        connection.close()
        return True
    except Exception as e:
        print(e)
        return False

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
                    return 400
                
                #creates the file localy
                path = os.path.join(app.config['UPLOAD_PATH'], filename)
                uploaded_file.save(path)
                # writes the file in a bucket
                file_id = str(uuid.uuid4())
                bucket_name = "video-bucket-storage"
                if upload_blob(file_id,path,bucket_name):
                    createQueueTask(file_id)
                    os.remove(path)
                return {'task':'file sent'},201
            else:
                return 400



# TODO: set up endpoint for setting status

api.add_resource(VideoConverter, '/upload')
api.add_resource(HomePage, '/')

if __name__ == '__main__':
    app.run(debug=True)

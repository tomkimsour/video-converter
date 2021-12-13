from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful import reqparse
import os
from werkzeug.utils import secure_filename
import pika

app = Flask(__name__)
# max file upload value set to 500 mB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 500
# allowed extensions
app.config['UPLOAD_EXTENSIONS'] = ['.mp4', '.mkv', '.mov','.webm','.wmv','.avi','.avchd']
# path to the writting folder
app.config['UPLOAD_PATH'] = 'output'
api = Api(app)

# rabbitMQ setup
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['PRODUCTION_RABBITMQCLUSTER_SERVICE_HOST'], credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)
connection.close()

class HomePage(Resource):
    def get(self):
        return {"text": "welcome"},200

class VideoConverter(Resource):
    def post(self):
        print(request)
        for uploaded_file in request.files.getlist('file'):
            print(uploaded_file)
            if uploaded_file.filename != '':
                # sanitize file name
                filename = secure_filename(uploaded_file.filename)
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    return 400
                print("received file :", filename)
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        return {'task':'file sent'},201

class Test(Resource):
    def get(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['PRODUCTION_RABBITMQCLUSTER_SERVICE_HOST'], credentials=credentials))
        channel = connection.channel()

        channel.basic_publish(exchange='',
                            routing_key='task_queue',
                            body='Hello World!',
                            properties=pika.BasicProperties(
                                delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE
                            ))
        print(" [x] Sent 'Hello World!'")
        connection.close()

        return {'task':'workload sent'},201

# TODO: set up endpoint for setting status

api.add_resource(VideoConverter, '/upload')
<<<<<<< HEAD
api.add_resource(Test, '/test')

=======
api.add_resource(HomePage, '/')
>>>>>>> fdae99baf625b653391fbb52a169e4bc2d88ec1a
if __name__ == '__main__':
    app.run(debug=True)

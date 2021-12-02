from flask import Flask
from flask.wrappers import Request
from flask_restful import Resource, Api
from flask_restful import reqparse

app = Flask(__name__)
api = Api(app)


# video_send_args = reqparse.RequestParser()
# video_send_args.add_argument('video')

class VideoConverter(Resource):
    def post(self):
        print(Request.files)
        # args = video_send_args.parse_args()
        # print(args)
        return {'task':'File sent'},201

api.add_resource(VideoConverter, '/upload')

if __name__ == '__main__':
    app.run(debug=True)
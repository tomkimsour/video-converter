from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful import reqparse
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
# max file upload value set to 500 mB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 500
# allowed extensions
app.config['UPLOAD_EXTENSIONS'] = ['.mp4', '.mkv', '.mov','.webm','.wmv','.avi','.avchd']
# path to the writting folder
app.config['UPLOAD_PATH'] = 'output'
api = Api(app)


class VideoConverter(Resource):
    def post(self):
        for uploaded_file in request.files.getlist('file'):
            if uploaded_file.filename != '':
                # sanitize file name
                filename = secure_filename(uploaded_file.filename)
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    return 400
                
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            else:
                return 400
        return {'task':'File sent'},201

api.add_resource(VideoConverter, '/upload')

if __name__ == '__main__':
    app.run(debug=True)
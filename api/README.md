# Description
This api allows to upload one video and tell which format you want to send back.
Then provides a link to download the converted file.

The application also sets up a connection to a RabbitMQ message queue.

# Installation
```
python3 venv env
source env/bin/activate
pip install -r requirements.txt
```

# Run
If you're already in the virtual environment you can skip the first line
```
source env/bin/activate
python3 api.py
```

# Tests Endpoints
First make sure the api is already running 
```
chmod +x endpointTest.sh
./endpointTest.sh
```
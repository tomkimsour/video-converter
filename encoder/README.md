# Description
Video encoder worker. It receives a message from a pod, fetches the video file in a local storage change format and write it in another local storage.

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
python3 converter.py
```

# Tests Endpoints
First make sure the api is already running 
```
chmod +x conversionTest.sh
./conversionTest.sh
```

# To do
 - Use cluster storage
 - Send status ???
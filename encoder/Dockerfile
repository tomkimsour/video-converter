FROM python:3.8-slim-buster
ENV PYTHONUNBUFFERED=1
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get -y update
RUN apt-get install -y ffmpeg
COPY . .
CMD ["python3", "converter.py"]
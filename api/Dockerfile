FROM python:3.8-slim-buster
ENV FLASK_APP=api.py PYTHONUNBUFFERED=1
EXPOSE 5000
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]
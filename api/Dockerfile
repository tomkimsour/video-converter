FROM python:3.8-slim-buster
ENV FLASK_APP=api.py PYTHONUNBUFFERED=1 GOOGLE_APPLICATION_CREDENTIALS="august-tesla-333012-9c128488d3c3.json"
EXPOSE 5000
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]
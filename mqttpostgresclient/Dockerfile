FROM arm32v7/python:3
#FROM frankwolf/rpi-python3:latest
#FROM resin/rpi-raspbian:latest
#FROM python:3.6.1-alpine
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
CMD ["python", "app/run_mqtt_client.py"]

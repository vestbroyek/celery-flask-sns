from celery import Celery
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)
app.config["CELERY_BROKER_URL"] = "redis://localhost:6379"

celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)

def msg_process(msg, tstamp):
    js = json.loads(msg)
    msg = 'Region: {0} / Alarm: {1}'.format(
        js['Region'], js['AlarmName']
    )
    # do stuff here, like calling your favorite SMS gateway API

@celery.task()
def say_hello(i):
    return f"Hello from Flask for the {i}-th time!" 

@app.route('/', methods=['POST', 'GET'])
def add_task():
    for i in range(100):
        say_hello.delay(i)
    return jsonify({'status': 'ok'})

@app.route('/sns', methods = ['GET', 'POST', 'PUT'])
def sns():
    # AWS sends JSON with text/plain mimetype
    try:
        js = json.loads(request.data)
    except:
        pass

    hdr = request.headers.get('X-Amz-Sns-Message-Type')
    # subscribe to the SNS topic
    if hdr == 'SubscriptionConfirmation' and 'SubscribeURL' in js:
        r = requests.get(js['SubscribeURL'])

    if hdr == 'Notification':
        msg_process(js['Message'], js['Timestamp'])

    return 'Hello from Flask!'

if __name__ == '__main__':
    app.run(
        host = "0.0.0.0",
        port = 5001,
        debug = True
    )


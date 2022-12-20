import base64
import boto3
import requests
import json
import os

def handler(event, context):
    session = boto3.session.Session(region_name='ru-central1')
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net'
    )
    bucket_id = event['messages'][0]['details']['bucket_id']
    object_id = event['messages'][0]['details']['object_id']
    folder_id = event['messages'][0]['event_metadata']['folder_id']
    token = context.token['access_token']

    photo = s3.get_object(Bucket=bucket_id, Key=object_id)
    encoded_photo = encode_file(photo['Body'])

    headers = {'Authorization': 'Bearer ' + token}
    stt_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'

    r = requests.post(
        url = stt_url,
        headers = headers,
        data = json.dumps(body_json(encoded_photo), indent=4)
    )

    faces = json.loads(r.content.decode('utf-8'))['results'][0]['results'][0]['faceDetection']['faces']

    sqs_session = boto3.session.Session(
        region_name='ru-central1',
        aws_access_key_id=os.environ['SQS_AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['SQS_AWS_SECRET_KEY']
    )
    sqs_client = sqs_session.client(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1'
    )

    queue_url = os.environ['QUEUE_URL']

    for face in faces:
        message = json.dumps({
            'origin_key': object_id,
            'vertices': face['boundingBox']['vertices']
        })
        sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=message
        )

    return {
        'statusCode': 200,
        'body': 'Hello World!',
    }

def encode_file(file):
    file_content = file.read()
    return base64.b64encode(file_content)

def body_json(encoded_photo):
    body_json = {
        'folderId': 'b1gfksas7ia01jo735nc',
        'analyze_specs': [{
            'content': encoded_photo.decode('utf-8'),
            'features': [{
            'type': "FACE_DETECTION"
            }]
        }]
    }
    return body_json

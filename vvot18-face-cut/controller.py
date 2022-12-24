from sanic import Sanic
from sanic.response import text
from sanic import response
import json
import os
import ydb
import ydb.iam
import requests
import random
import boto3
import io
from PIL import Image, ImageDraw

app = Sanic(__name__)
ydb_driver: ydb.Driver

def get_driver():
    endpoint = os.environ['DB_ENDPOINT']
    path = os.environ['DB_PATH']
    credentials = ydb.iam.MetadataUrlCredentials()
    driver_config = ydb.DriverConfig(
        endpoint, path, credentials=credentials
    )
    return ydb.Driver(driver_config)

def process_photo(body):
  photo_session = boto3.session.Session(
    region_name='ru-central1'
  )
  s3_photo_client = photo_session.client(
      service_name='s3',
      endpoint_url='https://storage.yandexcloud.net'
  )

  params = json.loads(json.loads(body.decode('utf-8'))['messages'][0]['details']['message']['body'])
  origin_key = params['origin_key']
  vertices0 = (int(params['vertices'][0]['x']), int(params['vertices'][0]['y']))
  vertices2 = (int(params['vertices'][2]['x']), int(params['vertices'][2]['y']))

  photo_data = io.BytesIO()
  s3_photo_client.download_fileobj(os.environ['PHOTO_BUCKET_ID'], origin_key, photo_data)

  photo_image = Image.open(photo_data)

  img1 = ImageDraw.Draw(photo_image)
  img1.rectangle([vertices0, vertices2],outline ="blue", width=5)
  face_photo_title = "{0}_{1}.jpg".format(
    origin_key.replace(".", ""),
    random.getrandbits(64)
  )

  in_mem_file = io.BytesIO()
  photo_image.save(in_mem_file, format='JPEG')
  in_mem_file.seek(0)

  s3_photo_client.upload_fileobj(in_mem_file, os.environ['FACES_BUCKET_ID'], face_photo_title, ExtraArgs={'ContentType': 'image/jpeg'})
  return [origin_key, face_photo_title]

def insert_entry_in_db(photo_key, photo_face_key):
    query = f"""
        PRAGMA TablePathPrefix("{os.environ['DB_PATH']}");
        INSERT INTO photo_faces (id, photo_key, face_key)
        VALUES ({random.getrandbits(32)}, '{photo_key}', '{photo_face_key}');
    """
    session = ydb_driver.table_client.session().create()
    session.transaction().execute(query, commit_tx=True)
    session.closing()


@app.after_server_start
async def after_server_start(app, loop):
    print(f"App listening at port {os.environ['PORT']}")
    global ydb_driver
    ydb_driver = get_driver()
    ydb_driver.wait(timeout=5)

@app.route("/", methods=["POST"],)
async def index(request):
    print("Hello from /")
    result = process_photo(request.body)
    insert_entry_in_db(result[0], result[1])
    return text("Hello")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ['PORT']), motd=False, access_log=False)
    print("Hello from main")


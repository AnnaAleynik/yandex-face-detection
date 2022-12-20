from sanic import Sanic
from sanic.response import text
from sanic import response
import json
import os
import ydb
from PIL import Image, ImageDraw

app = Sanic(__name__)

def process_photo(params):
  photo_session = boto3.session.Session(
    region_name='ru-central1'
  )
  s3_photo_client = photo_session.client(
      service_name='s3',
      endpoint_url='https://storage.yandexcloud.net'
  )

  params = json.loads(json.loads(request.body.decode('utf-8'))['messages'][0]['details']['message']['body'])
  origin_key = params['origin_key']
  vertices0 = (int(params['vertices'][0]['x']), int(params['vertices'][0]['y']))
  vertices2 = (int(params['vertices'][2]['x']), int(params['vertices'][2]['y']))

  photo_data = io.BytesIO()
  s3_photo_client.download_fileobj(os.environ['PHOTO_BUCKET_ID'], origin_key, photo_data)

  photo_image = Image.open(photo_data)

  img1 = ImageDraw.Draw(photo_image)
  img1.rectangle([vertices0, vertices2],outline ="blue", width=5)
  face_photo_title = "{0}_{1}_{2}_{3}_{4}.jpg".format(
    origin_key,
    vertices0[0],
    vertices0[1],
    vertices2[0],
    vertices2[1]
  )

  in_mem_file = io.BytesIO()
  photo_image.save(in_mem_file, format=photo_image.format)
  in_mem_file.seek(0)

  s3_faces_client.upload_fileobj(in_mem_file, os.environ['FACES_BUCKET_ID'], face_photo_title)
  return [origin_key, face_photo_title]

@app.after_server_start
async def after_server_start(app, loop):
    print(f"App listening at port {os.environ['PORT']}")

@app.route("/", methods=["POST"],)
async def index(request):
    print("Hello from /")
    params = json.loads(json.loads(request.body.decode('utf-8'))['messages'][0]['details']['message']['body'])
    origin_key = params['origin_key']
    vertices = params['vertices']

    

    return text("Hello")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ['PORT']), motd=False, access_log=False)
    print("Hello from main")


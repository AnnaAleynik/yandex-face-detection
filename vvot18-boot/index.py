import os
import json
import ydb
import ydb.iam
import requests

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

def func_response(code = 200, body = ''):
    return {'statusCode': code, 'body': body }


def get_driver():
    endpoint = os.environ['DB_ENDPOINT']
    path = os.environ['DB_PATH']
    credentials = ydb.iam.MetadataUrlCredentials()
    driver_config = ydb.DriverConfig(
        endpoint, path, credentials=credentials
    )
    return ydb.Driver(driver_config)


def update_name_in_db(ydb_driver, photo_key, photo_face_key, name):
    query = f"""
        PRAGMA TablePathPrefix("{os.environ['DB_PATH']}");
        UPDATE photo_faces
        SET user_chat_id = {user_chat_id}
        WHERE id = {entry_id};
    """
    session = ydb_driver.table_client.session().create()
    session.transaction().execute(query, commit_tx=True)
    session.closing()


def find_empty_face(ydb_driver):
    query = f"""
        PRAGMA TablePathPrefix("{os.environ['DB_PATH']}");
        SELECT id, face_key from photo_faces
        WHERE name IS NULL LIMIT 1;
    """
    session = ydb_driver.table_client.session().create()
    result_set = session.transaction().execute(query, commit_tx=True)
    session.closing()
    if not result_set or not result_set[0].rows:
        return None

    return result_set[0].rows[0]


def set_user_chat_id(ydb_driver, entry_id, message_in):
    user_chat_id = message_in['chat']['id']
    query = f"""
        PRAGMA TablePathPrefix("{os.environ['DB_PATH']}");
        UPDATE photo_faces
        SET user_chat_id = {user_chat_id}
        WHERE id = {entry_id};
    """
    session = ydb_driver.table_client.session().create()
    result_set = session.transaction().execute(query, commit_tx=True)
    session.closing()

    return 1


def send_message(text, message):
    message_id = message['message_id']
    chat_id = message['chat']['id']
    reply_message = {'chat_id': chat_id,
                     'text': text,
                     'reply_to_message_id': message_id}
    requests.post(url=f'{TELEGRAM_API_URL}/sendMessage', json=reply_message)


def send_photo(photo_url, message):
    message_id = message['message_id']
    chat_id = message['chat']['id']
    reply_message = {'chat_id': chat_id,
                     'photo': photo_url,
                     'reply_to_message_id': message_id}
    requests.post(url=f'{TELEGRAM_API_URL}/sendPhoto', json=reply_message)


def message_text(message):
    text = message["text"]
    return text


def empty(text):
    return text == None or len(text) == 0


def find(name, ydb_driver, message_in):
    query = f"""
        PRAGMA TablePathPrefix("{os.environ['DB_PATH']}");
        SELECT id, photo_key from photo_faces
        WHERE name = '{name}';
    """
    session = ydb_driver.table_client.session().create()
    result_set = session.transaction().execute(query, commit_tx=True)
    session.closing()

    if not result_set or not result_set[0].rows:
        send_message('Фотографии с {name} не найдены', message_in)
        return None

    for i in result_set[0].rows:
        photo_url = f'{os.environ.get("API_GATEWAY")}/photo?id={i["photo_key"].decode("utf-8")}'
        send_photo(photo_url, message_in)


def get_face(ydb_driver, message_in):
    entry = find_empty_face(ydb_driver)

    if entry:
        set_user_chat_id(ydb_driver, entry['id'], message_in)
        photo_url = f'{os.environ.get("API_GATEWAY")}/?face={entry["face_key"].decode("utf-8")}'
        send_photo(photo_url, message_in)
    else:
        send_message("There's no photo with unknown face", message_in)


def set_name(ydb_driver, message_in, name):
    user_chat_id = message_in['chat']['id']

    query = f"""
        PRAGMA TablePathPrefix("{os.environ['DB_PATH']}");
        SELECT id from photo_faces
        WHERE name IS NULL AND user_chat_id = {user_chat_id} LIMIT 1;
    """
    session = ydb_driver.table_client.session().create()
    result_set = session.transaction().execute(query, commit_tx=True)
    if not result_set or not result_set[0].rows:
        session.closing()
        return None

    entry_id = result_set[0].rows[0]['id']
    mutation = f"""
        PRAGMA TablePathPrefix("{os.environ['DB_PATH']}");
        UPDATE photo_faces
        SET name = '{name}'
        WHERE id = {entry_id};
    """
    session.transaction().execute(mutation, commit_tx=True)
    session.closing()


def handler(event, context):
    ydb_driver = get_driver()
    ydb_driver.wait(timeout=5)
    try:
        if TELEGRAM_BOT_TOKEN is None:
            return func_response()

        message_in = json.loads(event['body'])['message']
        message_txt = message_text(message_in)

        if empty(message_txt):
            return func_response()

        if "entities" in message_in:
            match message_txt.split()[0]:
                case "/find":
                    find(" ".join(message_txt.split()[1:]), ydb_driver, message_in)
                    return
                case "/getFace":
                    get_face(ydb_driver, message_in)
                    return
        else:
            set_name(ydb_driver, message_in, message_txt)
        
        return func_response()
    except Exception as err:
        print("Error")
        print(err)
        return func_response(body = err)

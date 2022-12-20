Алейник Анна 11-903, ИТИС 2022, Cloud Computing

Задание 2. Обработка фотографий с лицами людей

Настройка инфраструктуры через веб-приложение Yandex Cloud

1. Создайте приватный бакет `itis-2022-2023-vvot00-photos` в сервисе Object Storage.
1. Создайте приватный бакет `itis-2022-2023-vvot18-faces` в сервисе Object Storage.
2. Создайте сервисный аккаунт с ролью `storage.admin` и статический ключ для него.
3. Создайте сервисный аккаунт с ролью `viewer editor` (`sa-tasks`) и статический ключ для него.

4. В сервисе Message Queue создайте очередь `vvot18-tasks`
- Тип: стандартная

5. В сервисе Cloud Functions создайте облачную функцию `vvot18-face-detection` (среда выполнения Python), используя код из файла `vvot18-face-detection/vvot18-face-detection.py`.
Далее в редакторе функции:
6. Создайте файл `requirements.txt`, используя содержимое файла `vvot18-face-detection/requirements.txt`.
7. Создайте сервисный аккаунт с ролью `ai.vision.user` и привяжите его к функции в редакторе.
8. Добавьте следующие переменный окружения:
- AWS_ACCESS_KEY_ID = key_id (2)
- AWS_SECRET_ACCESS_KEY = key (2)
- SQS_AWS_ACCESS_KEY_ID = key_id (3)
- SQS_AWS_SECRET_KEY = key (3)
- QUEUE_URL = url for `vvot18-tasks`


9. Создайте сервисный аккаунт с ролью `serverless.functions.invoker` (`vvot-18-photo-tr`)
10. В сервисе Cloud Functions/Triggers создайте триггер `vvot18-photo-trigger`.
- Базовые параметры
    - Тип: `Object Storage`
    - Запускаемый ресурс: `Функция`
- Настройки Object Storage:
    - Бакет: `itis-2022-2023-vvot00-photos`
    - Типы событий: `Создание объекта`
    - Суффикс ключа объекта: `jpg`
- Настройки функции:
    - Функция: `vvot18-face-detection`
    - Тег версии функции: `$latest`
    - Сервисный аккаунт: сервисный аккаунт, созданный на шаге 7.

11. В сервисе Managed service for YDB создайте базу данных.
    - Тип Serverless
    - ```
        create table photo_faces(
            Id Utf8,
            Name Utf8,
            PhotoKey Utf8,
            FaceKey Utf8,
            CreatedAt Datetime,
            PRIMARY KEY (Id)
        );
    ```

11. Сервисный аккаунт `sa-vvot18-face-cutter` `container-registry.images.puller editor`
11. В сервисе Serverless Containers создайте контейнер `vvot18-face-cut` 
  - В сервисе Container Registry создайте реестр
  - Создайте образ на основе `vvot18-face-cut/controller.py`
  - `yc container registry configure-docker`
  - docker tag image_name:latest cr.yandex/#{id реестра}/image_name:latest
  - docker pull cr.yandex/#{id реестра}/image_name:latest
  - выберите образ в редакторе контейнера
  - Добавьте переменные окружения
    - PHOTO_BUCKET_ID - бакет с оригинальными фотографиями
    - FACES_BUCKET_ID - бакет для фотографий с найденными лицами
    - AWS_ACCESS_KEY_ID = key_id (2)
    - AWS_SECRET_ACCESS_KEY = key (2)



  <!-- docker buildx build --platform linux/amd64 . -t test-python -->
  <!-- docker run -it -e PORT=2222 -p 2222:2222 facecontroller -->

12. В сервисе Cloud Functions/Triggers создайте триггер `vvot18-task-trigger`.
- Базовые параметры
    - Тип: `Message Queue`
    - Запускаемый ресурс: `Контейнер`
- Настройки сообщений Message Queue:
    - Очередь сообщений: `vvot18-tasks`
    - Сервисный аккаунт: сервисный аккаунт c ролью `editor`. (sa-vvot18-task-tr)
- Настройки контейнера:
    - Контейнер 10
    - Сервисный аккаунт с ролью `serverless.containers.invoker` (sa-vvot18-faces-cut-invoker)

13. 
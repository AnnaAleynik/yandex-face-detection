Алейник Анна 11-903, ИТИС 2022, Cloud Computing

Задание 2. Обработка фотографий с лицами людей

Настройка инфраструктуры через веб-приложение Yandex Cloud

1. Создайте приватный бакет `itis-2022-2023-vvot00-photos` в сервисе Object Storage.
2. Создайте приватный бакет `itis-2022-2023-vvot18-faces` в сервисе Object Storage.
3. Создайте сервисный аккаунт с ролью `storage.admin` и статический ключ для него.
4. Создайте сервисный аккаунт с ролью `viewer editor` (`sa-tasks`) и статический ключ для него.

5. В сервисе Message Queue создайте очередь `vvot18-tasks`
- Тип: стандартная

6. В сервисе Cloud Functions создайте облачную функцию `vvot18-face-detection` (среда выполнения Python 3.11), используя код из файла `vvot18-face-detection/index.py`.
Далее в редакторе функции:
7. Создайте файл `requirements.txt`, используя содержимое файла `vvot18-face-detection/requirements.txt`.
8. Создайте сервисный аккаунт с ролью `ai.vision.user` и привяжите его к функции в редакторе.
9. Добавьте следующие переменный окружения:
- AWS_ACCESS_KEY_ID = key_id (созданный на шаге 3)
- AWS_SECRET_ACCESS_KEY = key (созданный на шаге 3)
- SQS_AWS_ACCESS_KEY_ID = key_id (созданный на шаге 4)
- SQS_AWS_SECRET_KEY = key (созданный на шаге 4)
- QUEUE_URL = url for `vvot18-tasks`


10. Создайте сервисный аккаунт с ролью `serverless.functions.invoker` (`vvot-18-photo-tr`)
11. В сервисе Cloud Functions/Triggers создайте триггер `vvot18-photo-trigger`.
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
    - Сервисный аккаунт: сервисный аккаунт, созданный на шаге 10.

12. В сервисе Managed service for YDB создайте базу данных.
    - vvot00-db-photo-face
    - Тип Serverless
    - ```
        create table photo_faces(
            id Int64,
            name String,
            photo_key String,
            face_key String,
            user_chat_id Int64,
            PRIMARY KEY (id)
        );
    ```

13. Сервисный аккаунт `sa-vvot18-face-cutter` `container-registry.images.puller editor`
14. В сервисе Serverless Containers создайте контейнер `vvot18-face-cut` 
  - В сервисе Container Registry создайте реестр
  - Создайте образ на основе `vvot18-face-cut/controller.py` (`docker buildx build --platform linux/amd64 . -t test-python`)
  - Далее в консоли
  - `yc container registry configure-docker`
  - `docker tag image_name:latest cr.yandex/#{id реестра}/#{image_name}:latest`
  - `docker push cr.yandex/#{id реестра}/#{image_name}:latest`
  - выберите образ в редакторе контейнера
  - Добавьте переменные окружения
    - PHOTO_BUCKET_ID - бакет с оригинальными фотографиями
    - FACES_BUCKET_ID - бакет для фотографий с найденными лицами
    - AWS_ACCESS_KEY_ID = key_id (2)
    - AWS_SECRET_ACCESS_KEY = key (2)
    - DB_ENDPOINT - Эндпоинт
    - DB_PATH - Размещение базы данных
    - API_GATEWAY - url for api gateway

15. В сервисе Cloud Functions/Triggers создайте триггер `vvot18-task-trigger`.
- Базовые параметры
    - Тип: `Message Queue`
    - Запускаемый ресурс: `Контейнер`
- Настройки сообщений Message Queue:
    - Очередь сообщений: `vvot18-tasks`
    - Сервисный аккаунт: сервисный аккаунт c ролью `editor`. (sa-vvot18-task-tr)
- Настройки контейнера:
    - Контейнер (созданный ранее)
    - Сервисный аккаунт с ролью `serverless.containers.invoker` (sa-vvot18-faces-cut-invoker)

16. Создайте и сконфигурируйте API-шлюз.
    - Используйте конфигурацию из `vvot18-boot/api_gateway.yml`

17. В сервисе Cloud Functions создайте облачную функцию `vvot18-boot` (среда выполнения Python 3.11), используя код из файла `vvot18-face-detection/index.py`.
Далее в редакторе функции:
18. Создайте файл `requirements.txt`, используя содержимое файла `vvot18-face-detection/requirements.txt`.
19. Создайте сервисный аккаунт с ролью `serverless.functions.invoker editor`
20. Добавьте следующие переменный окружения:
- TELEGRAM_BOT_TOKEN
- DB_ENDPOINT
- DB_PATH
- API_GATEWAY

21. Создайте TG бота с помощью bot father. Запомните токен (TG_BOT_TOKEN)
Далее в консоли (привязываем бота к функции)
```
TG_BOT_TOKEN=#{TELEGRAM_BOT_TOKEN}
YCF_URL=#{function_url}
TG_URL="https://api.telegram.org/bot${TG_BOT_TOKEN}/setWebhook?url=${YCF_URL}"
curl -s ${TG_URL}
```


#### Примеры работы
![1](https://github.com/AnnaAleynik/yandex-face-detection/blob/main/imgs/ex_1.png)

![2](https://github.com/AnnaAleynik/yandex-face-detection/blob/main/imgs/ex_2.png)

![3](https://github.com/AnnaAleynik/yandex-face-detection/blob/main/imgs/ex_3.png)

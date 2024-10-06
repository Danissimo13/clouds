## Nginx

**Nginx ("engine x")** — это HTTP-сервер, обратный прокси сервер с поддержкой кеширования и балансировки нагрузки, TCP/UDP прокси-сервер, а также почтовый прокси-сервер.

В первую очередь было необходимо установить nginx.

Так как лабораторную работу я выполнял на локальной машине (macOS), то проще всего было установить nginx через пакетный менеджер **Homewbrew** примерно такой командой:
``brew install nginx``.

На сервере с Linux это можно сделать аналогично с помощью другого пакетного менеджера.

## Требования

1. Nginx должен работать по https c сертификатом
2. Принудительное перенаправление HTTP-запросов (порт 80) на HTTPS (порт 443) для обеспечения безопасного соединения.
3. Настройка alias для создания псевдонимов путей к файлам или каталогам на сервере.
4. Настройка виртуальных хостов для обслуживания нескольких доменных имен на одном сервере.
5. На сервере находится два сервиса, запросы к которым проксируются через nginx

## Сервисы

Для демонстрации работы nginx были созданы 2 простых сервиса на **Python Starlette**.

У каждого сервиса есть по одному эндпоинту, возвращающего простой json:


```json
monitor.com/monitoring -> {'message': 'INTERNAL_SERVER_ERROR', 'code': '500'}
pinger.com/ping -> {'message': 'OK', 'code': '200'}
```

Также оба сервиса возвращают json вида 
![server_response_example](./images/server_response_example.png)
по пустому пути

## Конфигурация Nginx

Nginx сконфигурирован следующим образом:

- принимает запросы на 80 порт и принудительно проксирует их на 433 в целях безопасности
- на 443 порту в зависимости от доменного имени траффик проксируется на соотвествующий сервер и порт **(pinger.ru:81 или monitoring.ru:82)**
- в случае несовпадения доменного имени (локально пошли на localhost) запрос проксируется на дефолтный сервер и возвращает страницу-заглушку

Итоговый nginx конфиг с комментариями:


```editorconfig
# кол-во рабочих процессов сервера - обычно равно числу ядер процессора - у меня 6
worker_processes 6;

events {}

http {
    # проксируем траффик с HTTP на HTTPS
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # проксируем HTTPS траффик на 1 сервер
    server {
        listen 443 ssl;
        server_name pinger.ru;

        # данные SSL сертификата
        ssl_certificate /usr/local/etc/nginx/ssl/nginx.crt;
        ssl_certificate_key /usr/local/etc/nginx/ssl/nginx.key;

        location / {
            # Пробрасываем исходный IP адрес и хост
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_pass https://localhost:81;
        }
    }
     # проксируем HTTPS траффик на 2 сервер
    server {
        listen 443 ssl;
        server_name monitor.ru;

        # данные SSL сертификата
        ssl_certificate /usr/local/etc/nginx/ssl/nginx.crt;
        ssl_certificate_key /usr/local/etc/nginx/ssl/nginx.key;

        location / {
            # Пробрасываем исходный IP адрес и хост
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_pass https://localhost:82;
        }
    }

    # проксируем оставшийся траффик на дефолтный сервер
    server {
        listen 443 ssl default_server;
        server_name _;

        # данные SSL сертификата
        ssl_certificate /usr/local/etc/nginx/ssl/nginx.crt;
        ssl_certificate_key /usr/local/etc/nginx/ssl/nginx.key;

        # возвращаем дефолтный файл-заглушку
        index index.html;
        location / {
            alias /Users/serkona/Desktop/Clouds/Lab1/;
        }
    }
}
```

## Примеры запросов

Ниже представлены примеры запросов к серверам через Nginx:
![default_response](./images/default_response.png)
![pinger_default](./images/pinger_default.png)
![pinger_ping](./images/pinger_ping.png)
![monitor_default](./images/monitor_default.png)
![monitor_monitoring](./images/monitor_monitoring.png)


## Детали и комментарии

### Nginx

Более правильной практикой было бы разделить nginx конфиги для разных сервисов по разным файлам (**sites-available/sites-enabled**), но так как сервисы просты и имеют аналогичный функционал, конкретно здесь нет такой потребности.

Итоговый конфиг nginx на моей локальной машине располагается в директории ```/usr/local/etc/nginx```, а логи nginx в ```/usr/local/var/log/nginx```

### Сертификаты
Так как сервисы и конфигурация не продовые, я не уделял большого внимания безопасности и просто использовал самподписанные сертификат и ключ к нему для поддержки HTTPS на серверах
Выполнил это с помощью openssl вот так:

```bash
 openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout service.key -out service.crt
```

### Запуск
Так как рассматриваемый пример учебный, я не создавал для него нормального окружения (например не поднимал docker контейнеров),
а просто запустил 2 сервиса и nginx в терминале вот так (скрипт run.sh):
```bash
python3 server1.py &
python3 server2.py &
nginx
```

Также для обращения к доменным именам pinger.ru и monitor.ru локально необходимо было отредактировать файл ```etc/hosts```, добавив в него следущие строки:
```
127.0.0.1       pinger.ru
127.0.0.1       monitor.ru
```


## Вывод

Nginx - достаточно мощный и удобный инструмент, который будет полезным во многих сценариях.

В процессе выполнения лабораторной работы удалось глубже погрузиться в работу с nginx, научиться конфигурировать прокси сервер.

Несмотря на то, что полученная конфигурация и сервисы достаточно базовые, в процессе их написания удалось узнать много нового и полезного о nginx.







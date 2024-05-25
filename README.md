# Проект "Foodgram"

Добро пожаловать в наш проект **Foodgram**! 

Проект доступен по доменному имени 

[https://yafoodpract.ddns.net/](https://yafoodpract.ddns.net/)

## О проекте

Проект "Foodgram" - это сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии, которые использовались при создании проекта

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)


#### Запуск проекта

- Склонировать репозиторий

```bash
   git clone git@github.com:evashokom/foodgram.git
```

- В корневой директории проекта создать файл с переменными окружения (см. пример env.example) 

- Запустить проект локально

``` bash
    docker compose -f infra/docker-compose.yml up -d --build  
```

После выполнения этих шагов проект будет запущен и станет доступен по адресу [localhost](http://localhost/).



#### Наполнение БД данными

- Ингредиенты

```bash
   docker compose -f infra/docker-compose.yml exec backend python manage.py import_data
```

- Тэги (необходимо создать несколько тегов вручную через админку)


#### Workflow проекта

- **запускается при выполнении команды git push**
- **tests:** проверка кода на соответствие PEP8.
- **build_and_push_to_docker_hub:** сборка и размещение образа проекта на DockerHub.
- **deploy:** автоматический деплой на боевой сервер и запуск проекта.
- **send_massage:** отправка уведомления пользователю в Телеграм.

#### Документация и примеры запросов

Изучить примеры запросов можно в спецификации API по адресу http://localhost/api/docs/ после запуска проекта.

#### Надеемся, вам у нас понравится!

---

##### Проект подготовила evashokom с большой помощью и подержкой команды помощи и сопровождения Яндекс.Практикума. 

Если у вас возникнут вопросы, пожелания и предложения, вы можете обращаться к авторам этого проекта. Присылайте ваши письма на наш почтовый адрес __*www.foodgram@yandex.com*__. Будем рады видеть вашу обратную связь! 


# Aviary

To start
```
docker-compose up -d --build
```

To stop
```
docker-compose down
```

To perform db migrations
```
docker exec -it aviary-web-1 python manage.py makemigrations


ocker exec aviary-web-1 python manage.py migrate
```
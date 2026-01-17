# Yandex_Diploma

  version: '3.8'
  services:
    db:
      image: postgres:15
      environment:
        POSTGRES_DB: foodgram
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: postgres
      ports:
        - "5432:5432"
      volumes:
        - pgdata:/var/lib/postgresql/data/

    backend:
      build:
        context: ../backend
        dockerfile: Dockerfile
      environment:
        DJANGO_SECRET_KEY: "django-insecure-tl6c2r!qdu%45b!yn-xc!$!hxk(u%0044^+s_^o^(q=gl!%wq7"
      command: >
        sh -c "
        until nc -z db 5432; do echo 'Waiting for postgres...'; sleep 1; done;
        python manage.py migrate &&
        python manage.py collectstatic --noinput &&
        gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
        "
      volumes:
      - static_volume:/app/backend/foodgram/static
      depends_on:
        - db

    frontend:
      build:
        context: ../frontend
        dockerfile: Dockerfile
      volumes:
        - ../frontend:/app/result_build/

    nginx:
      image: nginx:1.19.3
      ports:
        - "80:80"
      volumes:
        - ./nginx.conf:/etc/nginx/conf.d/default.conf
        - ../frontend/build:/usr/share/nginx/html/
        - static_volume:/usr/share/nginx/html/static 
        - ./docs/:/usr/share/nginx/html/api/docs/
      depends_on:
        - backend


  volumes:
    pgdata:
      driver: local
    static_volume:
      driver: local 




    server {
        listen 80;

        location /api/docs/ {
            root /usr/share/nginx/html;
            try_files $uri $uri/redoc.html;
        }

        location /api/ {
            proxy_pass         http://backend;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto $scheme;
        }


        location /admin/ {
            proxy_pass         http://backend;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto $scheme;
        }



        location /static/ {
            alias /usr/share/nginx/html/static/;
        }




        location / {
            root /usr/share/nginx/html;
            index  index.html index.htm;
            try_files $uri /index.html;
        }

        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }

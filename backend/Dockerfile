FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn    

COPY . /app/backend

WORKDIR /app/backend/foodgram

RUN python manage.py collectstatic --noinput

EXPOSE 8000


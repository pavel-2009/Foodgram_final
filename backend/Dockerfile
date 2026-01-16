FROM python:3.13-slim

WORKDIR /app/foodgram

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN python manage.py collectstatic --noinput

CMD ["sh", "-c", "python manage.py migrate && gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000"]

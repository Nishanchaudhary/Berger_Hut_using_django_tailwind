FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt  requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]


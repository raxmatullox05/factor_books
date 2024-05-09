FROM python:3-alpine

ENV BOT_TOKEN=''

WORKDIR /app

COPY . /app
RUN pip install -r requirements.txt

CMD ["python3", "app.py"]
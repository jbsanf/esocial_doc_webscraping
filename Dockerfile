FROM python:3.11.4-alpine3.18

WORKDIR /app

VOLUME /data

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "./bot.py"]
FROM python:3.7-stretch

WORKDIR /opt

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "bot.py"]

FROM balenalib/raspberry-pi-python:3-latest

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app .
EXPOSE 5000

CMD [ "python", "./app.py" ]

FROM python:slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000
ENV FAUXAPI_APISECRET=testsecret
ENV FAUXAPI_APIKEY=testkey
ENV HOST_ADDRESS=192.168.1.1
ENV HOST_PORT=468

CMD [ "python", "./app.py" ]
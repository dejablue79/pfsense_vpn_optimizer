FROM python:slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000
ENV fauxapi-secret=PFFApRKMIQWl0HV5HbDsvQKJ
ENV fauxapi-key=JOTkJxThIEvjPfTdRxX0kDFzQtK7bOYCDpbCZfPjzsM6Y9ba5mfz6AuhTqsP
ENV host-address=192.168.1.1
ENV host-port=468

CMD [ "python", "./app.py" ]
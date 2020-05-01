FROM python:slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000
ENV FAUXAPI_SECRET=[CHANGE]
ENV FAUXAPI_KEY=[CHANGE]
ENV HOST_ADDRESS=[CHANGE]
ENV HOST_PORT=[CHANGE]

CMD [ "python", "./app.py" ]
FROM hassioaddons/base-python-armv7:5.3.3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app .
EXPOSE 5000

CMD [ "python3", "./app.py" ]

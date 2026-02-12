FROM python:3.9

RUN mkdir /app
WORKDIR /app
COPY . /app
RUN mkdir -p logs
RUN pip install -r requirements.txt

EXPOSE 8989
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
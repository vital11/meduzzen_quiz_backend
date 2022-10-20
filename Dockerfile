FROM python:3.10-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

EXPOSE ${SERVER_PORT}

CMD ["uvicorn", "app.main:app", "--host", "${SERVER_HOST}", "--port", "${SERVER_PORT}","--reload"]

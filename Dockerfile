FROM python:3.12

WORKDIR /code

RUN apt-get update && apt-get install -y make

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /code/

RUN uv sync

COPY . .

FROM python:3.11-slim-bookworm


RUN apt update && apt install -y build-essential libpq-dev
COPY requirements.txt .
RUN pip install --upgrade pip


ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y tzdata libpq-dev \
    && apt-get install -y binutils libproj-dev curl

RUN pip install --upgrade pip setuptools wheel
RUN pip install pydantic_core && pip install -r requirements.txt

COPY ./start_docker.sh /start_docker.sh
RUN chmod +x /start_docker.sh
WORKDIR /code
COPY . /code
RUN addgroup library && adduser --system --no-create-home library --ingroup library
RUN chown library:library -R /code

USER library
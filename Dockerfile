FROM python:3.12-alpine

WORKDIR /srv 

ENV PYTHONDONTWRITEBYTECODE=1  
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get -y install netcat gcc postgresql libpq-dev\
  && apt-get clean

COPY ./pyproject.toml ..
COPY ./poetry.lock ..

RUN pip install poetry  
RUN poetry install  

COPY src .

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "6"]
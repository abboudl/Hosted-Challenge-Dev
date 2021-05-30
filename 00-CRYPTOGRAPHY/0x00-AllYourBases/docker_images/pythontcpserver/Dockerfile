FROM python:3.7-slim

LABEL maintainer="Brandon West"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /usr/src/app/

WORKDIR /usr/src/app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
    
CMD python3.7 challenge.py 0.0.0.0 3000

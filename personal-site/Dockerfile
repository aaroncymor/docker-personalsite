# pull offical base image
FROM python:3.8.3-alpine

# set work directory
RUN mkdir -p /opt/services/personalsite
WORKDIR /opt/services/personalsite


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc \
    python3-dev musl-dev zlib-dev \
    jpeg-dev 

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/opt/services/personalsite/entrypoint.sh"]

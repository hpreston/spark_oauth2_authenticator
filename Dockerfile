FROM python:2-alpine
MAINTAINER Hank Preston <hank.preston@gmail.com>
EXPOSE 5000

# These environment Variables must be set when running container
ENV CLIENT_ID && \
ENV CLIENT_SECRET && \
ENV SERVER_ADDRESS

# Install basic utilities
RUN apk add -U \
        ca-certificates \
  && rm -rf /var/cache/apk/* \
  && pip install --no-cache-dir \
          setuptools \
          wheel

RUN mkdir /app
ADD ./requirements.txt /app
WORKDIR /app
RUN pip install --requirement ./requirements.txt

COPY ./spark_oauth_app_py.py /app

CMD [ "python", "spark_oauth_app_py.py" ]

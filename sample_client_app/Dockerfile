FROM python:2-alpine
MAINTAINER Hank Preston <hank.preston@gmail.com>
EXPOSE 5001

# These environment Variables must be set when running container
ENV CLIENT_ID && \
ENV AUTHENTICATOR_URL && \
ENV APP_ADDRESS

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

COPY ./client.py /app

CMD [ "python", "client.py" ]

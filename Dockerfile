FROM ubuntu:16.04

WORKDIR /code

RUN apt-get update && \
    apt-get install -y apt-transport-https curl python3-dev nginx && \
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    touch /etc/apt/sources.list.d/kubernetes.list && \
    echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list && \
    apt-get update && \
    apt-get install -y kubectl=1.11.1-00

COPY . /code

RUN chmod +x map_services.py entrypoint.sh

ENTRYPOINT sh entrypoint.sh

FROM alpine:3.9

ENV KUBE_LATEST_VERSION="v1.13.0"

RUN echo 'http://nl.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories \
    && apk add --update kubernetes python3 \
    && mkdir -p /root/.kube \
    && rm -rf /usr/bin/kubelet \
              /usr/bin/kubeadm \
              /usr/bin/kube-scheduler \
              /usr/bin/kube-proxy \
              /usr/bin/kube-controller-manager \
              /usr/bin/kube-apiserver \
              /usr/bin/hyperkube

COPY . /code
WORKDIR /code

RUN chmod +x map_services.py entrypoint.sh

ENTRYPOINT sh entrypoint.sh

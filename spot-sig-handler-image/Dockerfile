FROM alpine:3.16.2
RUN apk add --no-cache curl ca-certificates
RUN curl -f -s -o /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/arm64/kubectl && \
    chmod +x /usr/local/bin/kubectl && \
    kubectl version --client
RUN apk -Uuv add groff less py-pip bash
RUN pip install awscli
ADD start.sh /usr/local/bin/start.sh
ENTRYPOINT ["/usr/local/bin/start.sh"]

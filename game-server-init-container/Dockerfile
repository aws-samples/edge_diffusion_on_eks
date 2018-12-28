FROM openjdk:8u171-jre-alpine

RUN apk add --no-cache -U \
          lsof \
          vim \
          bash \
          curl iputils wget \
          python python-dev py2-pip

RUN pip install mcstatus ec2-metadata boto3

COPY start* /

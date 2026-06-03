FROM apache/flink:1.19.0-scala_2.12-java17

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python

COPY flink-jobs/requirements.txt .
RUN pip3 install -r requirements.txt

COPY infrastructure/flink-lib/*.jar /opt/flink/lib/

USER flink

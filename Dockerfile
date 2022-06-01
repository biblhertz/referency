FROM alpine/git AS x3mlDownloader
WORKDIR /
# download x3ml and lock version
RUN git clone https://github.com/SmartUPDS/x3ml.git && \
    cd /x3ml/ && \
    git checkout f31cf8a7becbad049725b7a34733719554279281

FROM alpine/git AS meTypesetDownloader
WORKDIR /
# download meTypeset and lock version
RUN git clone https://github.com/MartinPaulEve/meTypeset && \
    cd /meTypeset/ && \
    git checkout f5a8bf3eaad2ec14f52fa380050e743b1df39abe

FROM maven:3.6.3-openjdk-8-slim as x3mlJar
WORKDIR /
COPY --from=x3mlDownloader /x3ml/ ./
RUN mvn clean package

FROM ubuntu:18.04
WORKDIR /

RUN apt-get -y update && apt-get -y install openjdk-8-jre-headless python3 python3-pip
COPY --from=x3mlJar /target/x3ml-engine-1.9.5-3-smart-SNAPSHOT-exejar.jar ./x3ml/x3ml.jar
COPY --from=meTypesetDownloader /meTypeset ./meTypeset

#COPY . /refhar
WORKDIR /refhar
COPY requirements.txt requirements.txt
# python is python3 and install requirements
RUN ln -T /usr/bin/python3 /usr/bin/python && python3 -m pip install -r requirements.txt

ENV FLASK_APP: app.py
ENV FLASK_RUN_HOST=0.0.0.0

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8




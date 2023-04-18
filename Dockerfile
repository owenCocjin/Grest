FROM debian:latest
RUN mkdir /opt/Grest && apt-get -y update && apt-get -y upgrade && apt-get -y install python3 nano
WORKDIR /opt/Grest
COPY . /opt/Grest
CMD ["python3","/opt/Grest/main.py"]
EXPOSE 8080
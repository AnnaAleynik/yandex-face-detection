FROM ubuntu

RUN apt update && apt install -y python3 python3-pip
RUN pip3 install Sanic
RUN pip3 install requests
RUN pip3 install ydb==2.10.0
RUN pip3 install six
RUN pip3 install Pillow
RUN pip3 install boto3

COPY controller.py /

CMD ["python3", "/controller.py"]

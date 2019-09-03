FROM debian:sid
RUN echo 'deb http://mirrors.psu.ac.th/debian/ sid main contrib non-free' > /etc/apt/sources.list
RUN echo 'deb http://mirror.kku.ac.th/debian/ sid main contrib non-free' >> /etc/apt/sources.list
RUN apt update && apt upgrade -y
RUN apt install -y python3 python3-dev python3-pip python3-venv npm

COPY . /app
WORKDIR /app

RUN pip3 install flask uwsgi marshmallow
RUN python3 setup.py develop
RUN npm install --prefix pichayon/web/static

ENV PICHAYON_WEB_SETTINGS=/app/pichayon-production.cfg


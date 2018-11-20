#  Recommender
FROM python:3.6
# Install Python and Package Libraries
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean
RUN apt-get install -y \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    net-tools \
    nano \
    vim
# Project Files and Settings
ARG PROJECT=recommender_service
ARG PROJECT_DIR=/opt/recommender/${PROJECT}
RUN mkdir -p $PROJECT_DIR
WORKDIR $PROJECT_DIR
RUN pip install virtualenv
RUN virtualenv /opt/pyenv/myplex3.5/
RUN /bin/dash /opt/pyenv/myplex3.5/bin/activate
ADD . $PRPROJECT_DIR
RUN pip install -r requirements.txt
# Server
#ENV PRODUCTION true
EXPOSE 3306
EXPOSE 8001:8001
STOPSIGNAL SIGINT
COPY script/start.sh /start.sh
CMD ["sh","/start.sh"]

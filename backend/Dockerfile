FROM python:3.6.2

ENV PYTHONUNBUFFERED 1

#ARG UID=0
#ENV USER=ubuntu
#RUN useradd -u $UID -ms /bin/bash $USER

RUN mkdir -p /usr/src/backend

# Copy ImageMagick library source, compile and install:
COPY ./files/ImageMagick.tar.gz /usr/src/ImageMagick.tar.gz
RUN tar xzf /usr/src/ImageMagick.tar.gz -C /usr/src/
RUN cd /usr/src/ImageMagick-7.0.8-20 && ./configure && make --silent && make install --silent && ldconfig /usr/local/lib
RUN rm -rf /usr/src/ImageMagick-7.0.8-20

# Update working directory
WORKDIR /usr/src/backend

# copy requirements before any other code to create a more stable layer with python deps
COPY ./backend/requirements.txt /usr/src/backend/requirements.txt

# Upgrade pip
RUN pip install --upgrade pip

# Install the Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# copy everything from this directory to server/flask docker container
COPY ./backend /usr/src/backend

# Give execute permission to below file, so that the script can be executed by docker.
RUN chmod 777 /usr/src/backend/entrypoint.sh
RUN chmod -R 660 /usr/src/backend/static

# COPY uswgi.ini
COPY ./backend/uwsgi.ini /etc/uwsgi.ini

EXPOSE 5000

#USER ubuntu

CMD ["uwsgi", "--ini",  "/etc/uwsgi.ini"]

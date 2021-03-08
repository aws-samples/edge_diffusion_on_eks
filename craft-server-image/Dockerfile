FROM python:2.7
RUN apt-get update -y
RUN apt-get install -y sqlite3 
RUN /usr/local/bin/python -m pip install --upgrade pip
ADD deps /deps
ADD src /src
ADD server.py /server.py
ADD server-36-python.py /server-36-python.py
ADD world.py /world.py
RUN gcc -std=c99 -O3 -fPIC -shared -o world -I src -I deps/noise deps/noise/noise.c src/world.c
RUN pip install requests boto3
RUN mkdir -p /game/state
ADD craft.db /game/state/craft.db

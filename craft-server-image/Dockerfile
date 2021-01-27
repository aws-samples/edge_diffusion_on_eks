FROM python:2.7
RUN apt-get update -y
ADD deps /deps
ADD src /src
ADD server.py /server.py
ADD world.py /world.py
RUN gcc -std=c99 -O3 -fPIC -shared -o world -I src -I deps/noise deps/noise/noise.c src/world.c
RUN pip install requests
RUN mkdir -p /game/state
ADD craft.db /game/state/craft.db
CMD ["python", "/server.py"]

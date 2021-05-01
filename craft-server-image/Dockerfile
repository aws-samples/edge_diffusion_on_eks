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
RUN pip install requests boto3 psycopg2
ADD craft.db /craft.db

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN mkdir /root/.aws
COPY config /root/.aws

ADD save-state.sh /save-state.sh

CMD ["python","/server.py"]

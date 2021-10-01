FROM postgres:12.1

RUN apt-get update
RUN apt-get install -y software-properties-common wget
RUN add-apt-repository -y ppa:ubuntugis/ppa
RUN apt-get install -y postgresql-12-postgis-3

COPY schema/*.sql /docker-entrypoint-initdb.d/

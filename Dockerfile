# Base image: ubuntu:22.04
FROM ubuntu:22.04


ARG TARGETPLATFORM=linux/amd64,linux/arm64
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y wget gnupg software-properties-common curl git python3-pip && \
    wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - && \
    echo "deb https://debian.neo4j.com stable latest" > /etc/apt/sources.list.d/neo4j.list && \
    apt-get update && \
    apt-get install -y neo4j &&\
    apt-get autoremove -y && apt-get clean



RUN pip3 install --upgrade pip && \
    pip3 install pandas pyarrow neo4j




WORKDIR /infgarph_project


RUN mkdir -p /var/lib/neo4j/import && \
    wget -O /var/lib/neo4j/import/yellow_tripdata_2022-03.parquet \
    https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-03.parquet



RUN echo "dbms.default_listen_address=0.0.0.0" >> /etc/neo4j/neo4j.conf && \
    echo "dbms.default_advertised_address=localhost" >> /etc/neo4j/neo4j.conf && \
    echo "dbms.security.auth_enabled=true" >> /etc/neo4j/neo4j.conf



RUN mkdir -p /var/lib/neo4j/data/dbms && \
    neo4j-admin dbms set-initial-password


EXPOSE 7474 7687


CMD bash -c "\
    neo4j start && \
    for i in {1..10}; do \
        echo 'Waiting for Neo4j to start... attempt '$i; \
        cypher-shell -u neo4j -p infgarph_project 'RETURN 1;' && break; \
        sleep 5; \
    done && \
    python3 /infgarph_project/data_loader.py && \
    echo 'Data loaded successfully. Neo4j running at http://localhost:7474' && \
    tail -f /dev/null"
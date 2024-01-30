#!/bin/bash

if docker ps --filter "neo4j" -q >/dev/null 2>&1; then
    echo "Container is running!"
else
docker run \
    --name neo4j \
    -p7474:7474 \
    -p7687:7687 \
    -d \
    --rm \
    -v /data/neo4j/data:/data \
    -v /data/neo4j/logs:/logs \
    -v /data/neo4j/import:/var/lib/neo4j/import \
    -v /data/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/password \
    neo4j:latest
fi

#!/bin/bash

if docker ps --filter "name=neo4j" -q >/dev/null 2>&1; then
    docker exec -it neo4j cypher-shell -u neo4j -p password
else
    echo "Neo4j is not running"
fi

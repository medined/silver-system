#!/bin/bash

if docker ps --filter "name=neo4j" -q >/dev/null 2>&1; then
    docker stop neo4j
    docker rm neo4j
fi

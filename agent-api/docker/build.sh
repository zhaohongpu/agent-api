#!/bin/bash


docker stop agent-api
docker rm agent-api

docker build --progress=plain -t jerry9916/agent-api:latest -f docker/Dockerfile .

# docker run --name="agent-backend" -d -p 8188:8088 -v "/etc/localtime:/etc/localtime" -v "/Users/xiajie01/Develop/acg/agent-backend/log:/root/app/log" jerry9916/agent-backend:latest

#rm -rf agent-backend.tar
#docker save -o agent-backend.tar jerry9916/agent-backend:${VERSION}
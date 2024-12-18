#!/bin/bash

rm -rf ./agent-api ./*.tar.gz

mkdir -p agent-api/log agent-api/data/cache agent-api/data/fault_by_event_id agent-api/data/fault_by_index

cp *.py *.txt *.sh agent-api/

cp -r api demo service third docker agent-api/

tar -czf agent-api.tar.gz agent-api

rm -rf ./agent-api
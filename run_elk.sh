#!/bin/bash

# Start the ELK stack
docker-compose up -d

# Wait for the stack to be ready
echo "Waiting for ELK stack to start..."
sleep 60

# Open a bash terminal in the logstash container
docker exec -it logstash bash
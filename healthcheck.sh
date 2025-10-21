#!/bin/bash
while true; do
    curl -k https://localhost/health/ > /dev/null
    sleep 30
done

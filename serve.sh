#!/bin/bash

# Run the server directly from terminal, because setting up docker takes too much time now
export SS_STATIC_WEBPATH="./frontend/dist"
export SS_SERVER_PORT=80

source venv/bin/activate
nohup python3 ./server.py &
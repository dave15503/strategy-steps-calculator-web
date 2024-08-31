#!/bin/bash

source .env.sh

if ! [ -v LOCAL ]; then
    echo "Please set the environment file with your values: \$LOCAL as a boolean whether to deploy or not, \$SERVER_IP with the deployment IP in a .env.sh file"
    exit
fi

if [ $LOCAL = 1 ]; then 
    echo "Building for local deployment (used for docker image testing)"
    SERVER_IP=http://localhost
else 
    # ServerIP should have been set in the env file
    if ! [ -v SERVER_IP ]; then
        echo "set the ServerIP in the .env.sh file"
        exit
    fi
fi


SERVER_PORT=80

cd frontend
npm i
echo "Building Solid.js app in staging mode. Server IP $SERVER_IP:$SERVER_PORT gets baked in here"
echo "VITE_BACKEND_SERVER_URI=$SERVER_IP:$SERVER_PORT" > .env.staging
npx vite build --mode staging 
cd ..
docker build -t strategy-steps --build-arg SERVER_PORT=$SERVER_PORT .

# docker save -o dockerimage.tar strategy-steps
# scp dockerimage.tar root@$SERVER_IP:~/
# On Server
# docker load -i dockerimage.tar
# docker run --name strategy-steps -p 80:80 strategy-steps

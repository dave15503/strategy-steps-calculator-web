FROM python:3.12

WORKDIR /usr/src/app

ARG SERVER_PORT="80"

EXPOSE ${SERVER_PORT}

COPY ./server.py ./

# assumes `npm run build` has been run in staging mode
# otherwise the build has the wrong IP
COPY ./frontend/dist ./website

# configure python with the right paths to the website
ENV SS_STATIC_WEBPATH="./website"
ENV SS_SERVER_PORT=${SERVER_PORT}

# install python dependencies
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./server.py"]


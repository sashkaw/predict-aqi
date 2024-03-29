# syntax=docker/dockerfile:1
FROM python:3.9-slim

# Get environment variables from build args
ARG RUN_LOCAL_ARG
ENV RUN_LOCAL $RUN_LOCAL_ARG

ARG PROJECT_ID_ARG
ENV PROJECT_ID $PROJECT_ID_ARG

ARG GOOGLE_APPLICATION_CREDENTIALS_ARG
ENV GOOGLE_APPLICATION_CREDENTIALS $GOOGLE_APPLICATION_CREDENTIALS_ARG

# Set PORT number for server to listen on
ENV PORT=8080

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install NPM for React frontend
RUN apt-get update && apt-get install -y curl
RUN curl -s https://deb.nodesource.com/setup_16.x | bash
RUN apt-get -y install nodejs
#RUN npm install --prefix frontend

# Install requirements
#TODO - add venv
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENV DEBUG=1

# Run build script
CMD ["/bin/bash","-c","./build.sh"]
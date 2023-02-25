# syntax=docker/dockerfile:1
FROM python:3.9-slim

# Get environment variables from build args
ARG PROJECT_ID_ARG
ENV PROJECT_ID $PROJECT_ID_ARG

ARG GOOGLE_APPLICATION_CREDENTIALS_ARG
ENV GOOGLE_APPLICATION_CREDENTIALS $GOOGLE_APPLICATION_CREDENTIALS_ARG

# Set PORT number for server to listen on
ENV PORT=8080

# Set working directory
WORKDIR /app

# Install requirements
COPY requirements.txt requirements.txt
#TODO - add venv
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy files
COPY . .

ENV DEBUG=1

# Run build script
CMD ["/bin/bash","-c","./build.sh"]
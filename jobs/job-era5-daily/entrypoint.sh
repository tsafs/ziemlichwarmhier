#!/bin/bash

# Validate required environment variables
if [ -z "$CDS_API_KEY" ]; then
    echo "Error: CDS_API_KEY is not set."
    exit 1
fi

if [ -z "$ACCESS_KEY" ]; then
    echo "Error: ACCESS_KEY is not set."
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "Error: SECRET_KEY is not set."
    exit 1
fi

if [ -z "$ENDPOINT_URL" ]; then
    echo "Error: ENDPOINT_URL is not set."
    exit 1
fi

if [ -z "$BUCKET_NAME" ]; then
    echo "Error: BUCKET_NAME is not set."
    exit 1
fi

python src/process_daily.py

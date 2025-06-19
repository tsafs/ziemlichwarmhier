#!/bin/bash

# Get current date in YYYYMMDD format
TODAY=$(date +"%Y%m%d")

echo "Starting data collection and processing for date: $TODAY"

# 1. Fetch 10-minute station data
echo "Fetching 10-minute station data..."
python src/fetch_station_data.py --output-dir ./data --granularity 10min --type now

# 2. Extract and process the data
echo "Extracting and processing station data..."
python src/extract_10min_station_data.py --data-dir ./data --reference-date $TODAY --output-file ./data/10min_station_data_$TODAY.csv

# 3. Check if the output file was created
OUTPUT_FILE="./data/10min_station_data_${TODAY}.csv"
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Error: Output file $OUTPUT_FILE was not created!"
    exit 1
fi

echo "Data processing complete. Output saved to $OUTPUT_FILE"

# 4. Upload to S3
echo "Uploading processed data to S3..."

# Check if AWS credentials are set
if [ -z "$ACCESS_KEY" ] || [ -z "$SECRET_KEY" ] || [ -z "$BUCKET_NAME" ] || [ -z "$REGION" ] || [ -z "$ENDPOINT_URL" ]; then
    echo "Error: AWS credentials or bucket name not set. Please provide ACCESS_KEY, SECRET_KEY, BUCKET_NAME, REGION, and ENDPOINT_URL as environment variables."
    exit 1
fi

# Run the Python script for S3 upload
python_output=$(python src/upload_to_s3.py --file $OUTPUT_FILE --bucket "$BUCKET_NAME" --region "$REGION" --endpoint-url "$ENDPOINT_URL" 2>&1)
upload_exit_code=$?

if [ $upload_exit_code -eq 0 ]; then
    echo "Upload to S3 completed successfully."
    echo "$python_output"
else
    echo "Upload to S3 failed with exit code $upload_exit_code"
    echo "Error details:"
    echo "$python_output"
    exit $upload_exit_code
fi

echo "Job completed successfully!"

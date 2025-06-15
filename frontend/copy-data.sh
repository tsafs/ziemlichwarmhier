#!/bin/bash

# Create directory for data if needed
mkdir -p public

# Copy cities_metadata.csv to public folder
cp ../data/other/cities_metadata.csv public/

echo "Data files copied to public folder"

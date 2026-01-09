#!/bin/bash

# Store pytest arguments passed to this script
echo "📋 Using pytest arguments: $@"

# Create output directory for compatibility
mkdir -p ./output

# Execute pytest with allure results
# --alluredir: directory for allure results (for S3 upload)
# --junitxml: junit XML report (for analyze_result.py compatibility)
# -v: verbose output
pytest \
    --alluredir=$TMP_DIR/allure-results \
    --junitxml=./output/junit.xml \
    -v \
    "$@"

# Capture the exit code from pytest
exit_code=$?

# Copy junit.xml to TMP_DIR for S3 upload if needed
cp ./output/junit.xml $TMP_DIR/junit.xml 2>/dev/null || true

# Exit the shell script with the same exit code
exit $exit_code

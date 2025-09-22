#!/bin/bash

# Set AWS Lambda function name
FUNCTION_NAME="ordonnanceur_groupe2"
ROLE_ARN="arn:aws:iam::242201282704:role/LambdaS3Role-group2"
RUNTIME="python3.12"
ZIP_FILE="main.zip"
HANDLER="main.lambda_handler"

# AWS Lambda Layer Configuration
LAYER_NAME="package_groupe2"
# LAYER_ZIP="layer_content.zip"
LAYER_ZIP="package_content.zip"

# AWS S3 Configuration
BUCKET_NAME="central-supelec-data-groupe2"

# Function to create an S3 bucket
create_bucket() {
    echo "Creating S3 bucket: $BUCKET_NAME..."
    aws s3 mb "s3://$BUCKET_NAME"

    if [ $? -eq 0 ]; then
        echo "Bucket $BUCKET_NAME created successfully!"
    else
        echo "Failed to create bucket."
        exit 1
    fi
}

# Function to delete an S3 bucket
delete_bucket() {
    echo "Deleting S3 bucket: $BUCKET_NAME..."
    aws s3 rb "s3://$BUCKET_NAME" --force

    if [ $? -eq 0 ]; then
        echo "Bucket $BUCKET_NAME deleted successfully!"
    else
        echo "Failed to delete bucket."
        exit 1
    fi
}

# Function to upload a file to S3
upload_file() {
    read -p "Enter the local file or folder path: " FILE_PATH

    if [ -d "$FILE_PATH" ]; then
        echo "Uploading folder: $FILE_PATH to S3 bucket: $BUCKET_NAME..."
        aws s3 cp "$FILE_PATH" "s3://$BUCKET_NAME/" --recursive
    elif [ -f "$FILE_PATH" ]; then
        echo "Uploading file: $FILE_PATH to S3 bucket: $BUCKET_NAME..."
        aws s3 cp "$FILE_PATH" "s3://$BUCKET_NAME/$FILE_PATH"
    else
        echo "Invalid path! Please enter a valid file or folder path."
    fi

    if [ $? -eq 0 ]; then
        echo "File uploaded successfully!"
    else
        echo "Failed to upload file."
        exit 1
    fi
}

# Function to download a file from S3
download_file() {
    read -p "Enter the file name in S3: " FILE_NAME
    read -p "Enter the destination path: " DEST_PATH

    echo "Downloading $FILE_NAME from S3 bucket: $BUCKET_NAME to $DEST_PATH..."
    aws s3 cp "s3://$BUCKET_NAME/$FILE_NAME" "$DEST_PATH"

    if [ $? -eq 0 ]; then
        echo "File downloaded successfully!"
    else
        echo "Failed to download file."
        exit 1
    fi
}

# Function to delete a file from S3
delete_file() {
    read -p "Enter the file name in S3 to delete: " FILE_NAME

    echo "Deleting $FILE_NAME from S3 bucket: $BUCKET_NAME..."
    aws s3 rm "s3://$BUCKET_NAME/$FILE_NAME"

    if [ $? -eq 0 ]; then
        echo "File deleted successfully!"
    else
        echo "Failed to delete file."
        exit 1
    fi
}

# Function to create Lambda Layer
create_layer() {
    echo "Publishing Lambda Layer: $LAYER_NAME..."
    LAYER_ARN=$(aws lambda publish-layer-version \
        --layer-name "$LAYER_NAME" \
        --content S3Bucket="$BUCKET_NAME",S3Key="$LAYER_ZIP" \
        --compatible-runtimes "$RUNTIME" \
        --query 'LayerVersionArn' --output text)

    if [ $? -eq 0 ]; then
        echo "Layer created successfully: $LAYER_ARN"
    else
        echo "Failed to create Lambda Layer."
        exit 1
    fi
}

# Function to create Lambda
create_lambda() {
    echo "Creating AWS Lambda function: $FUNCTION_NAME..."

    # Check if the layer exists before creating the function
    LAYER_ARN=$(aws lambda list-layer-versions --layer-name "$LAYER_NAME" --query 'LayerVersions[0].LayerVersionArn' --output text 2>/dev/null)

    if [ -z "$LAYER_ARN" ]; then
        echo "No existing layer found. Creating one..."
        create_layer
    fi

    aws lambda create-function \
        --function-name "$FUNCTION_NAME" \
        --runtime "$RUNTIME" \
        --role "$ROLE_ARN" \
        --zip-file "fileb://$ZIP_FILE" \
        --handler "$HANDLER" \
        --layers "$LAYER_ARN"

    if [ $? -eq 0 ]; then
        echo "Lambda function created successfully!"
    else
        echo "Failed to create Lambda function."
        exit 1
    fi
}

# Function to invoke Lambda with payload
invoke_lambda() {
    read -p "Enter file name: " FILE_NAME
    read -p "Enter number of cores: " NUM_CORES

    PAYLOAD="{\"file_name\": \"$FILE_NAME\", \"num_cores\": $NUM_CORES}"

    echo "Invoking AWS Lambda function: $FUNCTION_NAME with payload: $PAYLOAD..."

    aws lambda invoke \
        --function-name "$FUNCTION_NAME" \
        --payload "$PAYLOAD" \
         --cli-binary-format raw-in-base64-out \
        response.json

    if [ $? -eq 0 ]; then
        echo "Lambda function invoked successfully! Check response.json"
    else
        echo "Failed to invoke Lambda function."
        exit 1
    fi
}

update_lambda() {
    echo "Updating AWS Lambda function: $FUNCTION_NAME..."

    aws lambda update-function-code \
        --function-name  "$FUNCTION_NAME" \
        --zip-file "fileb://$ZIP_FILE"

    if [ $? -eq 0 ]; then
        echo "Lambda function updated successfully!"
    else
        echo "Failed to update Lambda function."
        exit 1
    fi
}

# Function to delete Lambda
delete_lambda() {
    echo "Deleting AWS Lambda function: $FUNCTION_NAME..."
    aws lambda delete-function \
        --function-name "$FUNCTION_NAME"

    if [ $? -eq 0 ]; then
        echo "Lambda function deleted successfully!"
    else
        echo "Failed to delete Lambda function."
        exit 1
    fi
}

# Function to delete Lambda Layer
delete_layer() {
    echo "Deleting Lambda Layer: $LAYER_NAME..."

    VERSIONS=$(aws lambda list-layer-versions --layer-name "$LAYER_NAME" --query 'LayerVersions[*].Version' --output text)

    if [ -z "$VERSIONS" ]; then
        echo "No existing layer versions found."
        return
    fi

    for VERSION in $VERSIONS; do
        echo "Deleting Layer Version: $VERSION..."
        aws lambda delete-layer-version --layer-name "$LAYER_NAME" --version-number "$VERSION"
    done

    echo "Lambda Layer deleted successfully!"
}

# Main Menu
while true; do
    echo "========================="
    echo "    AWS Lambda & S3 Manager   "
    echo "========================="
    echo "1) Create Lambda Function"
    echo "2) Invoke Lambda Function"
    echo "3) Update Lambda Function"
    echo "4) Delete Lambda Function"
    echo "5) Create Lambda Layer"
    echo "6) Delete Lambda Layer"
    echo "7) Create S3 Bucket"
    echo "8) Delete S3 Bucket"
    echo "9) Upload File to S3"
    echo "10) Download File from S3"
    echo "11) Delete File from S3"
    echo "12) Exit"
    read -p "Choose an option: " OPTION

    case $OPTION in
        1) create_lambda ;;
        2) invoke_lambda ;;
        3) update_lambda ;;
        4) delete_lambda ;;
        5) create_layer ;;
        6) delete_layer ;;
        7) create_bucket ;;
        8) delete_bucket ;;
        9) upload_file ;;
        10) download_file ;;
        11) delete_file ;;
        12) echo "Exiting..." && exit 0 ;;
        *) echo "Invalid option! Please choose again." ;;
    esac

    echo ""
done



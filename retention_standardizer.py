""" AWS Kinesis Video Stream (KVS) retention standardizer:
    This script standardizes the data retention period for KVS to 24 hours.
    It reads a list of KVS ARNs from a file, checks their current retention settings, and updates 
    them if necessary.
    Any streams that do not conform to the expected retention periods are logged for further review.
"""
import json
import boto3
import botocore.exceptions


# Set AWS params for boto
PROFILE = 'default'
REGION = 'us-east-1'

# Read-in ARN list
def main():
    """ Begins standardization process by ingesting ARNs from file """
    with open('files/kvs-arns.txt', 'r', encoding='utf-8') as arn_list:
        for arn in arn_list:
            arn = arn.strip() # EOL not being detected
            result = kvs_decisioning(arn)
            if result is False:
                print(f"Error processing ARN: {arn}")
                break


# Get version value, retention value, and disposition
# The "Version" value is required for updating the retention period
def kvs_decisioning(arn):
    """ Determine new retention value (if needed) based on current settings """
    session = boto3.Session(profile_name=PROFILE)
    
    client = session.client('kinesisvideo', region_name=REGION)
    response = client.describe_stream(
        StreamARN = arn
    )
    version = response['StreamInfo']['Version']
    retention = response['StreamInfo']['DataRetentionInHours']

    # Disposition based on existing retention
    if retention < 24:
        print("Increasing retention for:", arn)
        adjust_retention = 24 - retention
        return update_retention(arn, version, adjust_retention, defined=False)
    elif retention > 24:
        print("Decreasing retention for:", arn)
        adjust_retention = retention - 24
        return update_retention(arn, version, adjust_retention, defined=True)
    else:
        print("Retention is correct for:", arn)
        printer(arn, version, retention)
        return True


# Modify retention setting or die (this may happen due to excessive API calls)
def update_retention(arn, version, adjust_retention, defined):
    """ Update retention period to 24 hours """
    session = boto3.Session(profile_name=PROFILE)
    if defined is False:
        direction = 'INCREASE_DATA_RETENTION'
    else:
        direction = 'DECREASE_DATA_RETENTION'

    try:
        client = session.client('kinesisvideo', region_name=REGION)
        client.update_data_retention(
            StreamARN = arn,
            CurrentVersion = version,
            Operation = direction,
            DataRetentionChangeInHours = adjust_retention
        )
        with open('files/audit.txt', 'a+', encoding='utf-8') as file:
            file.write(arn + " - Success\n")
    except botocore.exceptions.ClientError as e: 
        with open('files/error.txt', 'a+', encoding='utf-8') as file:
            file.write(arn + " - " + str(e) + "\n")
        return False # Indicate failure
    return True


# If the retention period isn't one of the defaults we're expecting (0, 48), print the stream info
# out for further processing
def printer(arn, version, retention):
    """ Print stream info to JSON file """
    results = {"ARN:": arn, "Version:": version, "Retention:": retention}
    with open('files/kvs-version.json', 'a+', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii= True, indent=2)
        file.write('\n')


if __name__ == "__main__":
    main()

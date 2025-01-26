# Kinesis video streams (KVS) have a "Version" value which is required for updating the retention period and 
# possibly other fields which is separate from the ARN

# Read-in ARN list
def main():
    with open('kinesisVideo/files/kvs-arns.txt', 'r') as list:
        for arn in list:
            arn = arn.rstrip('\n') # EOL not being detected
            kvsGetVersion(arn)


# Get version value for ARN and inspect retention
def kvsGetVersion(arn):
    import boto3

    client = boto3.client('kinesisvideo')
    response = client.describe_stream(
        StreamARN = arn
    )
    version = response['StreamInfo']['Version']
    retention = response['StreamInfo']['DataRetentionInHours']

    # Disposition based on existing retention
    if retention == 0:
        updateRetention(arn, version, defined=False)
    elif retention == 48:
        updateRetention(arn, version, defined=True)
    else:
        printer(arn, version, retention)


# Just go ahead and do the needful
def updateRetention(arn, version, defined):
    import boto3

    if defined == False:
        direction = 'INCREASE_DATA_RETENTION'
    else:
        direction = 'DECREASE_DATA_RETENTION'

    client = boto3.client('kinesisvideo')
    response = client.update_data_retention(
        StreamARN = arn,
        CurrentVersion = version,
        Operation = direction,
        DataRetentionChangeInHours = 24
    )


# If the retention period isn't one of the defaults we're expecting (0, 48), print the stream info
# out for further processing
def printer(arn, version, retention):
    import json

    results = {"ARN:": arn, "Version:": version, "Retention:": retention}
    with open('kinesisVideo/files/kvs-version.json', 'a+', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii= True, indent=2)



if __name__ == "__main__":
    main()
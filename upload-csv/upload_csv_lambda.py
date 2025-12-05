import boto3
import csv
import io

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('csv_import')  # CHANGE IF NEEDED

def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    print("Bucket:", bucket)
    key = event['Records'][0]['s3']['object']['key']

    # Read the file from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')

    # Parse CSV
    csv_file = io.StringIO(content)
    reader = csv.DictReader(csv_file)

    for row in reader:
        print("Inserting row:", row)
        table.put_item(Item=row)

    return {"status": "success"}

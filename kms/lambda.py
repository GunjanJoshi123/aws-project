import json
import boto3
import base64
import uuid

kms = boto3.client('kms')
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('secure-notes-table')
KMS_KEY = "arn:aws:kms:us-east-1:800939197474:key/c42dc20c-6a78-4b06-a131-b721eec4afd6"

def lambda_handler(event, context):

    # Handle both direct and proxy request
    if "body" in event:
        body = json.loads(event["body"])
    else:
        body = event

    note = body["note"]

    encrypted = kms.encrypt(
        KeyId=KMS_KEY,
        Plaintext=note.encode()
    )

    ciphertext = base64.b64encode(
        encrypted["CiphertextBlob"]
    ).decode()

    note_id = str(uuid.uuid4())

    table.put_item(
        Item={
            "noteId": note_id,
            "encrypted_note": ciphertext
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Note stored",
            "noteId": note_id
        })
    }
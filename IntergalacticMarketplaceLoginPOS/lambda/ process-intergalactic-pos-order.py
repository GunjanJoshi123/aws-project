import json
import uuid
from datetime import datetime
import boto3

# DynamoDB table
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("IntergalacticPOSOrders")   # Your table name

def lambda_handler(event, context):
    try:
        print("Event received:", event)

        # Read body
        body = json.loads(event.get("body", "{}"))

        agent = body.get("agent")
        items = body.get("items")

        # Validate input
        if not agent or not items or len(items) == 0:
            return respond(400, {"error": "Invalid input. Agent or items missing."})

        # Generate order metadata
        order_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Create simple test signature
        signature = f"{order_id}-{timestamp}"

        # Store in DynamoDB
        table.put_item(
            Item={
                "order_id": order_id,
                "timestamp": timestamp,
                "agent": agent,
                "items": json.dumps(items),
                "signature": signature
            }
        )

        # Response to frontend
        return respond(200, {
            "result": "success",
            "order_id": order_id,
            "timestamp": timestamp,
            "signature": signature
        })

    except Exception as e:
        print("Error:", str(e))
        return respond(500, {"error": str(e)})


def respond(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        },
        "body": json.dumps(body)
    }

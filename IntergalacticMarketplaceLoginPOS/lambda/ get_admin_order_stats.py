import json
import boto3
from collections import Counter

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = "IntergalacticPOSOrders"
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        resp = table.scan()
        items = resp.get("Items", [])

        orders = []
        item_counts = Counter()
        total_items = 0

        for row in items:
            order_items = try_parse_json(row.get("items")) or try_parse_json(row.get("items_json")) or {}

            order = {
                "order_id": row.get("order_id"),
                "timestamp": row.get("timestamp"),
                "agent": row.get("agent"),
                "items": order_items
            }
            orders.append(order)

            for k, v in order_items.items():
                qty = int(v) if str(v).isdigit() else 0
                item_counts[k] += qty
                total_items += qty

        total_orders = len(orders)
        most_common = item_counts.most_common(3)

        result = {
            "total_orders": total_orders,
            "total_items": total_items,
            "per_item_counts": dict(item_counts),
            "most_ordered_top3": [{"item": it, "count": cnt} for it, cnt in most_common],
            "orders": orders
        }

        return respond(200, result)

    except Exception as e:
        return respond(500, {"error": str(e)})

def try_parse_json(v):
    if not v:
        return None
    if isinstance(v, dict):
        return v
    try:
        return json.loads(v)
    except:
        return None

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

# api/index.py - Simple home handler
def handler(request):
    """Simple home handler"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": '{"message": "LINE Bot API", "webhook": "/webhook"}'
    }

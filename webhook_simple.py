# Simple webhook test to diagnose the 500 error
from fastapi import FastAPI, Request, HTTPException
import uvicorn

app = FastAPI()

@app.get("/webhook")
async def webhook_get():
    """Test endpoint"""
    return {"status": "ok", "message": "Webhook is working"}

@app.post("/webhook")
async def webhook_post(request: Request):
    """Simple webhook that always returns 200"""
    try:
        # Get basic request info
        headers = dict(request.headers)
        body = await request.body()
        
        return {
            "status": "ok",
            "message": "Webhook received successfully",
            "body_size": len(body),
            "has_signature": "x-line-signature" in headers
        }
    except Exception as e:
        # Even if there's an error, return 200 to LINE
        return {
            "status": "error", 
            "message": str(e),
            "note": "But still returning 200 to prevent LINE webhook error"
        }

if __name__ == "__main__":
    print("Starting simple webhook test server...")
    print("URL: http://localhost:8000/webhook")
    uvicorn.run(app, host="0.0.0.0", port=8000)
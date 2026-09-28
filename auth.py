from fastapi import Header, HTTPException
import os

accessapikey = os.getenv("X_API_KEY")


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != accessapikey:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key



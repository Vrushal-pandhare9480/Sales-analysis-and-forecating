import random
import time
import os
import requests

from dotenv import load_dotenv

load_dotenv()

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# ======================================================
# CONFIG
# ======================================================

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("SMTP_EMAIL")

# Temporary OTP storage
otp_store = {}


# ======================================================
# BREVO EMAIL FUNCTION
# ======================================================

def send_email(receiver_email, subject, text_content):

    if not BREVO_API_KEY:
        raise Exception("BREVO_API_KEY is not configured")

    if not BREVO_SENDER_EMAIL:
        raise Exception("SMTP_EMAIL is not configured")

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    data = {
        "sender": {
            "name": "Sales Analysis & Forecasting",
            "email": BREVO_SENDER_EMAIL
        },
        "to": [
            {
                "email": receiver_email
            }
        ],
        "subject": subject,
        "textContent": text_content
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=20
    )

    if response.status_code not in [200, 201]:
        raise Exception(
            f"Brevo API Error: {response.status_code} - {response.text}"
        )


# ======================================================
# OTP EMAIL
# ======================================================

def send_otp_email(receiver_email, otp):

    send_email(
        receiver_email,
        "Sales Analysis & Forecasting - OTP",
        f"""
Hello,

Welcome to the Sales Analysis & Forecasting Project.

Your OTP is:

{otp}

This OTP is valid for 5 minutes.

Thank you.
"""
    )


# ======================================================
# REQUEST MODELS
# ======================================================

class SendOTPRequest(BaseModel):

    email: EmailStr


class VerifyOTPRequest(BaseModel):

    email: EmailStr

    otp: str


# ======================================================
# SEND OTP
# ======================================================

@router.post("/send-otp")
def send_otp(request: SendOTPRequest):

    # --------------------------------------------------
    # 1. GENERATE OTP
    # --------------------------------------------------

    otp = str(
        random.randint(100000, 999999)
    )

    # OTP expires after 5 minutes

    otp_store[request.email] = {

        "otp": otp,

        "expires": time.time() + 300

    }

    # --------------------------------------------------
    # 2. SEND OTP EMAIL
    # --------------------------------------------------

    try:

        send_otp_email(
            request.email,
            otp
        )

    except Exception as e:

        # Remove OTP if email could not be sent

        otp_store.pop(
            request.email,
            None
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to send OTP email: {str(e)}"
        )

    # --------------------------------------------------
    # 3. RESPONSE
    # --------------------------------------------------

    return {

        "success": True,

        "message":
            "OTP sent successfully"

    }


# ======================================================
# VERIFY OTP
# ======================================================

@router.post("/verify-otp")
def verify_otp(request: VerifyOTPRequest):

    user = otp_store.get(
        request.email
    )

    if not user:

        raise HTTPException(
            status_code=400,
            detail="OTP not found"
        )

    # --------------------------------------------------
    # CHECK EXPIRY
    # --------------------------------------------------

    if time.time() > user["expires"]:

        del otp_store[
            request.email
        ]

        raise HTTPException(
            status_code=400,
            detail="OTP expired"
        )

    # --------------------------------------------------
    # CHECK OTP
    # --------------------------------------------------

    if request.otp != user["otp"]:

        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    # --------------------------------------------------
    # SEND WELCOME EMAIL
    # --------------------------------------------------

    try:

        send_welcome_email(
            request.email
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to send welcome email: {str(e)}"
        )

    # OTP successfully verified

    del otp_store[
        request.email
    ]

    return {

        "success": True,

        "message":
            "Email verified successfully"

    }


# ======================================================
# WELCOME EMAIL
# ======================================================

def send_welcome_email(receiver_email):

    send_email(
        receiver_email,
        "Welcome to Sales Analysis & Forecasting",
        """
Hello,

Welcome to Sales Analysis & Forecasting!

Your email has been successfully verified.

You can now access the dashboard and explore:

• Sales Analysis
• Product Analytics
• Customer Analytics
• Regional Analysis
• Sales Forecasting

Thank you for using our Sales Analysis & Forecasting project.

Best Regards,
Sales Analysis & Forecasting Team
"""
    )
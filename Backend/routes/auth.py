import random
import time
import os


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


SMTP_EMAIL = os.getenv(
    "SMTP_EMAIL"
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD"
)


# Temporary OTP storage
otp_store = {}

import smtplib
from email.message import EmailMessage

def send_otp_email(receiver_email, otp):

    msg = EmailMessage()

    msg["Subject"] = "Sales Analysis & Forecasting - OTP"
    msg["From"] = SMTP_EMAIL
    msg["To"] = receiver_email

    msg.set_content(
        f"""
Hello,

Welcome to the Sales Analysis & Forecasting Project.

Your OTP is:

{otp}

This OTP is valid for 5 minutes.

Thank you.
"""
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:

        server.starttls()

        server.login(
            SMTP_EMAIL,
            SMTP_PASSWORD
        )

        server.send_message(msg)
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
    # 1. CAPTCHA CHECK
    # --------------------------------------------------


    # --------------------------------------------------
    # 2. GENERATE OTP
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
    # 3. TEMPORARY DEVELOPMENT RESPONSE
    # --------------------------------------------------

    send_otp_email(
    request.email,
    otp
)


    return {

        "success": True,

        "message":
            "OTP generated successfully"

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

    send_welcome_email(
    request.email
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

def send_welcome_email(receiver_email):

    msg = EmailMessage()

    msg["Subject"] = "Welcome to Sales Analysis & Forecasting"
    msg["From"] = SMTP_EMAIL
    msg["To"] = receiver_email

    msg.set_content(
        f"""
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

    with smtplib.SMTP("smtp.gmail.com", 587) as server:

        server.starttls()

        server.login(
            SMTP_EMAIL,
            SMTP_PASSWORD
        )

        server.send_message(msg)

print("SMTP EMAIL:", SMTP_EMAIL)
print("SMTP PASSWORD EXISTS:", SMTP_PASSWORD is not None)
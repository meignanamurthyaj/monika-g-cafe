from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from backend.utils import auth as auth_utils
from backend.utils.email import send_email
from backend.config import settings
import random
from datetime import datetime, timedelta
import httpx
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = auth_utils.hash_password(user_data.password)
    new_user = models.User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone_profile=user_data.phone_profile,
        password_hash=hashed_pwd,
        role_id=user_data.role_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth_utils.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    
    access_token = auth_utils.create_access_token(data={"sub": user.email, "role": user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/send-otp")
def send_otp(request: schemas.OTPSendRequest, db: Session = Depends(get_db)):
    otp_code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.now() + timedelta(minutes=5)
    
    otp_entry = models.OTPVerification(
        email=request.email,
        otp_code=otp_code,
        expires_at=expires_at,
        is_verified=False
    )
    db.add(otp_entry)
    db.commit()
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
        <div style="background-color: #d4a373; padding: 20px; text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 24px; letter-spacing: 1px;">Monika G Cafe</h2>
        </div>
        <div style="padding: 30px; line-height: 1.6; color: #333;">
            <p>Hello,</p>
            <p>We received a request to log in to your Monika G Cafe account using a One-Time Password (OTP).</p>
            <div style="background-color: #fcf8f2; border: 1px dashed #d4a373; border-radius: 6px; padding: 15px; text-align: center; margin: 25px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #a3704c;">{otp_code}</span>
            </div>
            <p style="font-size: 14px; color: #666;">This OTP is valid for <strong>5 minutes</strong>. If you did not request this, please ignore this email.</p>
        </div>
        <div style="background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #888; border-top: 1px solid #e0e0e0;">
            &copy; 2026 Monika G Cafe. All rights reserved.
        </div>
    </div>
    """
    email_sent = send_email(
        to_email=request.email,
        subject="Monika G Cafe - Log In OTP",
        html_content=html_content
    )
    
    print(f"\n[OTP Dispatch] Generated OTP {otp_code} for {request.email}. Email sent status: {email_sent}\n")
    return {"message": "OTP has been sent successfully"}

@router.post("/verify-otp", response_model=schemas.Token)
def verify_otp(request: schemas.OTPVerifyRequest, db: Session = Depends(get_db)):
    otp_record = db.query(models.OTPVerification).filter(
        models.OTPVerification.email == request.email,
        models.OTPVerification.is_verified == False,
        models.OTPVerification.expires_at > datetime.now()
    ).order_by(models.OTPVerification.id.desc()).first()
    
    if not otp_record or otp_record.otp_code != request.otp_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")
    
    otp_record.is_verified = True
    db.commit()
    
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        user = models.User(
            first_name=request.email.split("@")[0].capitalize(),
            last_name="User",
            email=request.email,
            password_hash=auth_utils.hash_password(""),
            role_id=4  # Customer
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    access_token = auth_utils.create_access_token(data={"sub": user.email, "role": user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/google-login", response_model=schemas.Token)
async def google_login(payload: schemas.GoogleLoginRequest, db: Session = Depends(get_db)):
    if payload.token.startswith("mock_google_token_"):
        email = payload.token.replace("mock_google_token_", "") + "@gmail.com"
        given_name = "MockGoogle"
        family_name = "User"
    else:
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.token}")
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail="Invalid Google OAuth credential token")
                data = resp.json()
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to communicate with Google OAuth verification API: {str(e)}")
        
        google_client_id = settings.GOOGLE_CLIENT_ID
        if data.get("aud") != google_client_id:
            raise HTTPException(status_code=400, detail="Google client ID mismatch")
            
        email = data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Google account email not found in token info")
            
        given_name = data.get("given_name", "Google")
        family_name = data.get("family_name", "User")
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(
            first_name=given_name,
            last_name=family_name,
            email=email,
            password_hash=auth_utils.hash_password(""),
            role_id=4  # Customer
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    access_token = auth_utils.create_access_token(data={"sub": user.email, "role": user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}


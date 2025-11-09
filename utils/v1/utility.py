import smtplib
import os
import secrets
import bcrypt
from email.message import EmailMessage
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from config.v1.config import Config


def sendEmail_background_task(receiver: str, subject: str, body: str):
    """
    Send an email in the background using Gmail SMTP with UTF-8 support.
    """
    try:
        msg = EmailMessage()
        msg["From"] = Config.SENDER_EMAIL
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.set_content(body)  # handles UTF-8 automatically

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
            server.send_message(msg)

        print("Link sent. ✅")
        return True

    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e} ❌")
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except Exception as e:
        print(f"General error occurred: {e} ❌")
        return JSONResponse(content={"error": str(e)}, status_code=400)


def sendResetLink(receiver, background_task, db, raw_token):
    from dao.v1.user_dao import user_databaseConnection

    try:
        data = user_databaseConnection.getUserTable(db)
        userID = None
        for i in data:
            if i.email == receiver:
                userID = i.id
                break
        if not userID:
            print("User not found.❌")
            return False

        subject = "Password Reset Request"
        body = f"""
Hi,

We received a request to reset your password. Please click the link below to reset it:

Reset your password: {Config.FRONTEND_URL}/{raw_token}

⚠️ This link will expire in 30 minutes and can only be used once.

If you did not request a password reset, please ignore this email.

Thank you,
FastVault Tech.
"""
        background_task.add_task(sendEmail_background_task, receiver, subject, body)
        return True
    except Exception as e:
        print(f"Link not sent.❌ {e}")
        return False


# def saveImage(image):
#     # Saving the uploaded image to the specified folder
#     image.save(os.path.join(UPLOAD_FOLDER, image.filename))


# def deleteFile(image):
#     try:
#         filePath = os.path.join(
#             UPLOAD_FOLDER, image.filename
#         )  # Constructing the file path
#         os.remove(filePath)  # Deleting the file
#     except FileNotFoundError as e:
#         pass  # Ignoring the exception if the file is not found


# def deletewithFilename(image):
#     try:
#         filePath = os.path.join(UPLOAD_FOLDER, image)  # Constructing the file path
#         os.remove(filePath)  # Deleting the file
#     except FileNotFoundError as e:
#         pass  # Ignoring the exception if the file is not found


def generate_reset_token():
    # Generate a secure random token (user sees this raw token)
    raw_token = secrets.token_urlsafe(32)

    # Hash the token before saving to DB
    hashed_token = bcrypt.hashpw(raw_token.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    # Set expiration (30 minutes)
    expires_at = datetime.utcnow() + timedelta(minutes=30)

    return raw_token, hashed_token, expires_at

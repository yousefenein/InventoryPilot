from rest_framework import serializers
from auth_app.models import users
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from backend.settings import FRONTEND_URL, EMAIL_HOST_USER
import logging

logger = logging.getLogger('WarehousePilot_app')

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = ('user_id','role','first_name', 'last_name', 'department')


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    # validate_email(): checks if email exists in db
    def validate_email(self, value):
        if not users.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    # save(): generates a password reset token and sends the email
    def save(self, email):
        email = email.strip()
        user = users.objects.get(email=email)

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.user_id))  # Use user_id (your PK)
        
        # Preparing values for email
        reset_url = f"{FRONTEND_URL}/reset-password/{uid}/{token}/"
        subject = "WarehousePilot - Password Reset Request"

        # Plain-text version of email (fallback)
        text_content = f"""
        Hello {user.first_name},

        You requested a password reset for your account ({user.username}).

        Click the link below to reset your password:
        {reset_url}

        Link expires in 24 hours.

        If you didn't request this, please ignore this email.

        Best regards,
        Warehouse Pilot Team       
        """

        # HTML version of email (styled)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset Request</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 0;
                    background-color: #f9fafb;
                }}
                .container {{
                    background-color: white;
                    border-radius: 0.5rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                    margin: 20px auto;
                }}
                .header {{
                    padding: 2rem;
                    text-align: center;
                    background-color: #950606;
                    color: white;
                }}
                .logo {{
                    height: 4rem;
                    margin-bottom: 1.5rem;
                }}
                .content {{
                    padding: 2rem;
                    text-align: center;
                }}
                h1 {{
                    font-size: 1.5rem;
                    font-weight: bold;
                    margin-bottom: 1rem;
                    color: #ffffff;
                }}
                p {{
                    font-size: 1rem;
                    color: #4b5563;
                    margin-bottom: 1.5rem;
                }}
                .button {{
                    display: inline-block;
                    padding: 0.75rem 1.5rem;
                    background-color: #111827;
                    color: white;
                    text-decoration: none;
                    border-radius: 0.375rem;
                    font-weight: 600;
                    font-size: 1rem;
                    margin: 1.25rem 0;
                    transition: background-color 0.2s;
                }}
                .button:hover {{
                    background-color: #1f2937;
                }}
                .footer {{
                    padding: 1.5rem;
                    text-align: center;
                    font-size: 0.875rem;
                    color: #ffffff;
                    background-color: #950606;
                    border-top: 1px solid #e5e7eb;
                }}
                .footer p {{
                    color: #ffffff;
                }}
                .link-text {{
                    word-break: break-all;
                    font-size: 0.75rem;
                    color: #950606;
                    margin: 1rem 0;
                    font-weight: 600;
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                
                <div class="content">
                    <p>Hello {user.first_name},</p>
                    
                    <p>You requested a password reset for your account (<strong>{user.username}</strong>).</p>  

                    <p>To reset your password, click the button below:</p>
                    
                    <a href="{FRONTEND_URL}/{uid}/{token}" class="button">Reset Password</a>
                    
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    
                    <p class="link-text">{FRONTEND_URL}/{uid}/{token}</p>
                    
                    <p>This link will expire in 24 hours for security reasons.</p>
                    
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
                
                <div class="footer">
                    <p >
                        Best regards,<br/>
                        <strong>Warehouse Pilot Team</strong>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        # Send email
        send_mail(
            subject=subject,
            message=text_content,
            html_message=html_content,
            from_email=EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

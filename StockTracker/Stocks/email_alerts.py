# email_alerts.py

import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from urllib import request

from .utils import generate_otp


def email_alert(subject, body, to,otp, api_key=None, image_paths=None):
    # Your email_alert function code goes here
    # Generate OTP



    # Update the email body to include the OTP
    body_with_otp = f"{body}\n\nYour OTP is: {otp}"

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = to


    # Create the body of the email
    text = MIMEText(body_with_otp)
    msg.attach(text)

    if image_paths:
        for image_path in image_paths:
            # Open the image file
            with open(image_path, 'rb') as img_file:
                # Attach the image to the email
                img = MIMEImage(img_file.read())
                img.add_header('Content-Disposition', 'attachment', filename=image_path)
                msg.attach(img)

    # Email credentials
    user = "stockbased9@gmail.com"
    password = "xawepsysrrnshdpk"

    # Connect to the SMTP server
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)

    # Send the email
    server.sendmail(user, to, msg.as_string())

    # Close the connection
    server.quit()



import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
import logging

# Configure logging similar to other modules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

def send_email(to_email, hashtag):
    # Get credentials from environment variables
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD').replace('"', "")

    from_name = "Threat Hunters - CyberShield Hackathon"
    subject = "Your Threat Inteliigence Report is Ready!"
    body = f"Dear User,\n\nPlease find attached the threat intelligence report for your requested hashtag - #{hashtag}.\n\nBest regards,\nThreat Hunters Team - CyberShield Hackathon"
    attachment_path = f"outputs/{hashtag}_report.pdf"

    if not gmail_user or not gmail_password:
        logging.error("Gmail credentials not found in environment variables")
        raise ValueError("Please set GMAIL_USER and GMAIL_APP_PASSWORD in .env file")

    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = from_name
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(body, 'plain'))

        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype=os.path.splitext(attachment_path)[1][1:])
                attachment.add_header('Content-Disposition', 'attachment', 
                                   filename=os.path.basename(attachment_path))
                msg.attach(attachment)
                logging.info(f"Attached file: {attachment_path}")
        elif attachment_path:
            logging.warning(f"Attachment file not found: {attachment_path}")

        # Create SMTP session
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
            
        logging.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False

def send_demo_email(to_email):
    # Get credentials from environment variables
    print(os.environ)
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD').replace('"', "")

    from_name = "Threat Hunters - CyberShield Hackathon"
    subject = "Your Threat Inteliigence Report is Ready!"
    body = f"Dear User,\n\nPlease find attached the demo threat intelligence report for your requested hashtag - #gazwaehind.\n\nBest regards,\nThreat Hunters Team - CyberShield Hackathon"
    attachment_path = f"sample_data/gazwaehind_report.pdf"

    if not gmail_user or not gmail_password:
        logging.error("Gmail credentials not found in environment variables")
        raise ValueError("Please set GMAIL_USER and GMAIL_APP_PASSWORD in .env file")

    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = from_name
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(body, 'plain'))

        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype=os.path.splitext(attachment_path)[1][1:])
                attachment.add_header('Content-Disposition', 'attachment', 
                                   filename=os.path.basename(attachment_path))
                msg.attach(attachment)
                logging.info(f"Attached file: {attachment_path}")
        elif attachment_path:
            logging.warning(f"Attachment file not found: {attachment_path}")

        # Create SMTP session
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
            
        logging.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False

def send_acknowledgment_email(to_email, hashtag):
    # Get credentials from environment variables
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD').replace('"', "")

    from_name = "Threat Hunters - CyberShield Hackathon"
    subject = "We have received your request!"
    body = f"Dear User,\n\nWe have successfully received your request for analyzing the hashtag - #{hashtag}. You will receive the report as soon as it is ready. We highly appreciate your patience till then!\n\nBest regards,\nThreat Hunters Team - CyberShield Hackathon"

    if not gmail_user or not gmail_password:
        logging.error("Gmail credentials not found in environment variables")
        raise ValueError("Please set GMAIL_USER and GMAIL_APP_PASSWORD in .env file")

    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = from_name
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(body, 'plain'))

        # Create SMTP session
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
            
        logging.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    recipient = "pnp14072005@gmail.com"
    
    success = send_email(recipient, "kashmirbanegapakistan")
    print("Email sent successfully" if success else "Failed to send email")
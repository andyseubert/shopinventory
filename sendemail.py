
import argparse
import os, re
import sys
import smtplib
 
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
 
 
## default vars
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
 
#arguments sent
parser = argparse.ArgumentParser(description='send an email')
parser.add_argument('-u','--username', help='username to auth with gmail with', required=True)
parser.add_argument('-p','--password', help='password  to auth with gmail with', required=True)
parser.add_argument('-s','--subject', help='subject of email', required=True)
parser.add_argument('-b','--body', help='body text of email', required=True)
parser.add_argument('-t','--to', help='send the message to this person',required=True)
parser.add_argument('-f','--from', help='send the message From this address',required=True)
#parser.add_argument('-a','--attach', help='full path to filename to attach', required=True)
args = vars(parser.parse_args())

sender = args['username']
password = args['password']
subject = args['subject']
message = args['body']
recipient = args['to']
sender = args['from']
#directory = args['attach'].lstrip()

def main():
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = recipient
    msg['From'] = sender
    #
    #files = os.listdir(directory)
    #gifsearch = re.compile(".jpg", re.IGNORECASE)
    #files = filter(gifsearch.search, files)
    #for filename in files:
    #    path = os.path.join(directory, filename)
    #    if not os.path.isfile(path):
    #        continue
    #
    #    img = MIMEImage(open(path, 'rb').read(), _subtype="jpg")
    #    img.add_header('Content-Disposition', 'attachment', filename=filename)
    #    msg.attach(img)
    #
    part = MIMEText('text', "plain")
    part.set_payload(message)
    msg.attach(part)
 
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
 
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(sender, password)
 
    session.sendmail(sender, recipient, msg.as_string())
    session.quit()
 
if __name__ == '__main__':
    main()
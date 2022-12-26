#Este modulo genera el informe ejecutivo
#y lo envia por email
import os
import json
import pytz
import smtplib, ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def email(users, config=None):
    if config is None:
        print("[EMAIL] No configuration provided")
        return []

    now = datetime.now(pytz.timezone('Europe/Madrid'))
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    dt_filestring = "autocracker-"+now.strftime("%d/%m/%Y-%H:%M:%S")+".txt"
    msg = MIMEMultipart()

    body = """\
    The following users have been reset:"""

    for user in users:
        body += """\

    {}""".format(user)

    try:
        data = config.getEmailConfig()
        host = data['host']
        port = data['port']
        username = data['username']
        password = data['password']
        to = data['to']

        msg['From'] = username
        msg['To'] = ", ".join(to)
        msg['Subject'] = "Autocracker report {}".format(dt_string)
        msg.attach(MIMEText(body, 'plain'))
        
        #Logs are an array of strings
        logs = config.log.getLogBuffer()
        if len(logs) > 0:
            log = MIMEBase('application', 'text')
            log.set_payload('\n'.join(logs))

            encoders.encode_base64(log)
            log.add_header(
                "Content-Disposition",
                f"attachment; filename= {dt_filestring}"
            )
            msg.attach(log)

        s = smtplib.SMTP(host, port)
        s.starttls()
        s.login(username, password)
        
        for recipient in to:
            config.log.info("[EMAIL] Sending email to {}".format(recipient))
            s.sendmail(username, recipient, msg.as_string())
        s.quit()

    except Exception as e:
        config.log.error("[EMAIL] Error: {}".format(e))

# Create a secure SSL context


import logging as logger
import os
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from scripts.utils.common_utils import CommonUtils

"""
*****************************************************************************************************************
email_utility = EmailUtility(USERNAME,PASSWORD,SERVER,PORT,ENCRYPTION)
mail_response = email_utility.mail_without_attachment(from_address,to,subject,text)
*****************************************************************************************************************
"""


class EmailUtility:
    def __init__(self, username, password, server, port, encryption):
        try:
            logger.debug(username + " " + password)
            logger.debug("inside the Email Utility____________________")
            if encryption == "SSL":
                self.mailserver = smtplib.SMTP_SSL(server, port)
                self.mailserver.login(username, password)
            elif encryption == "TLS":
                self.mailserver = smtplib.SMTP(server, port)
                self.mailserver.starttls()
            else:
                logger.debug("inside else")
                self.mailserver = smtplib.SMTP(server, port)
                self.mailserver.starttls()
            self.mailserver.login(username, password)
            logger.debug("connection established")
            logger.debug(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        except Exception as e:
            logger.debug(str(e))
            traceback.print_exc()
            logger.exception("connection failed" + str(e))

    def send_mail(self, subject, email_body, to_address, from_first="CPCB ", mail_type="plain", cc=True):
        response = {"status": "failed"}
        try:
            mail = MIMEMultipart()
            mail["Subject"] = subject
            if cc:
                mail["To"] = ", ".join(to_address)
            mail["From"] = from_first
            mail.attach(MIMEText(email_body, mail_type))
            response = self.mailserver.sendmail("CCR", to_address, mail.as_string())
            self.mailserver.quit()
            if response == {}:
                return_json = {"status_code": "success"}
                logger.debug("sending mail successful")
            else:
                return_json = {"status_code": "failed"}
                logger.debug("mail not sent")
            return return_json
        except Exception as e:
            logger.exception(e)
            logger.exception("mail not sent")
        return response

    def mail_without_attachment(self, from_address, to, subject, text):
        flag = False
        try:
            msg = MIMEMultipart()
            msg["From"] = from_address
            msg["To"] = ", ".join(to)
            msg["Subject"] = subject
            msg.attach(MIMEText(text))
            self.mailserver.sendmail(from_address, to, msg.as_string())
            self.mailserver.close()
            flag = True
        except Exception as e:
            logger.exception(str(e))
            traceback.print_exc()
        return flag

    def mail(self, email, type_txt="plain"):
        flag = False
        try:
            logger.debug("inside the mail definition")
            msg = MIMEMultipart()
            rcpt = email["cc"].split(",") + email["bcc"].split(",") + [email["to"]]
            logger.debug("get the rcpt list")
            msg["From"] = email["from"]
            msg["To"] = email["to"]
            msg["CC"] = email["cc"]
            msg["Subject"] = email["subject"]
            logger.debug("calling the attach function")
            msg.attach(MIMEText(email["body"], _subtype=type_txt))
            logger.debug("send the mail definition")
            self.mailserver.sendmail(email["from"], rcpt, msg.as_string())
            logger.debug("called the mail send definition")
            self.mailserver.close()
            flag = True
        except Exception as e:
            traceback.print_exc()
            logger.exception(str(e))
        return flag


class EmailError(Exception):
    pass


class FormulationToolEmailService:
    def __init__(self, url: str, digest_username: str, digest_password: str):
        self.url = url
        self.auth = (digest_username, digest_password)

    def send_mail(
        self, receivers_list: List[str], content: str, subject: str, project_id: str, from_name: str = "UnifyTwin"
    ) -> bool:
        email_payload = {
            "receiver_list": receivers_list,
            "from_name": from_name,
            "content": content,
            "subject": subject,
            "gateway_id": "priority",
        }

        header = {"projectId": project_id, "module": os.getenv("MODULE_NAME"), "tenantId": os.getenv("UT_TENANT_ID")}
        if CommonUtils.hit_external_service(
            api_url=self.url,
            payload=email_payload,
            auth=self.auth,
            headers=header,
            raise_error=True,
        ):
            logger.info("Email sent successfully")
            return True

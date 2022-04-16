import logging
# initialize the log settings
logging.basicConfig(filename='error_email.log', level=logging.INFO, filemode='w')
try:
    # libraries to be imported
    import time
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    import settings
    import functions

    def send_mail(fromaddr, toaddr, cc, mail_pass):
        # instance of MIMEMultipart
        msg = MIMEMultipart()
        # storing the senders email address
        msg['From'] = fromaddr
        # storing the receivers email address
        msg['To'] = toaddr
        # Cc
        msg['Cc'] = ", ".join(cc)

        # Mail to
        to = msg["To"].split(",") + msg["Cc"].split(",")
        # storing the subject
        msg['Subject'] = "Daily Attendance"
        # string to store the body of the mail
        body = "Here, I have attached a csv file which contains daily attendance of ishraak solutions"
        # attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))
        filename = str(common_functions.get_previous_date())

        attachment = open("Attendance/"+filename+".csv", "rb")
        # instance of MIMEBase and named as p
        p = MIMEBase('application', 'octet-stream')
        # To change the payload into encoded form
        p.set_payload((attachment).read())
        # encode into base64
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        # attach the instance 'p' to instance 'msg'
        msg.attach(p)
        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)
        # start TLS for security
        s.starttls()
        # Authentication
        s.login(fromaddr, mail_pass)
        # Converts the Multipart msg into a string
        text = msg.as_string()

        try:
            # sending the mail
            s.sendmail(fromaddr, to, text)
            print ('Successfully sent')
        except Exception as e:
            print(e)
            print ('Error sending mail')

        # terminating the session
        s.quit()

    if __name__ == '__main__':

        # Take input from setting
        mail_setting = settings.mail_setting()

        if mail_setting["Active"] == 1:
            while True:

                c_month, c_date, c_hour_minute, c_hour_minute_second = common_functions.get_current_date_time()
                if c_hour_minute in mail_setting["Times"]:
                    send_mail(mail_setting["From"], mail_setting["To"], mail_setting["Cc"], mail_setting["Password"])

                time.sleep(60.0)

except Exception as e:
    logging.exception(str(e))
"""code pasted from choregraphe box"""

import sys, os
import smtplib, email

class choregrapheMail(object):

    def mail(self, email_user, to, subject, text, attach, email_pwd, smtp, port):
        msg = email.MIMEMultipart.MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = to
        msg['Subject'] = subject

        msg.attach(email.MIMEText.MIMEText(text))

        if attach:
             part = email.MIMEBase.MIMEBase('application', 'octet-stream')
             part.set_payload(open(attach, 'rb').read())
             email.Encoders.encode_base64(part)
             part.add_header('Content-Disposition',
                               'attachment; filename="%s"' % os.path.basename(attach))
             msg.attach(part)

        if( port != "" ):
            mailServer = smtplib.SMTP(smtp, port)
        else:
            mailServer = smtplib.SMTP(smtp)

        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(email_user, email_pwd)
        mailServer.sendmail(email_user, to, msg.as_string())

        mailServer.close()


    def sendMessage(self,sText="text body"):
        print "preparing email..."
        sEmailUser = "itk.norma@outlook.dk"
        aTo = "andkr@aarhus.dk"
        sSubject = "Pepper service alert"
        sAttachedFilePath = ""
        sPwd = "kjhg3298f!(4"
        sSmtp = "smtp-mail.outlook.com"
        sPort = 587
        try:
            sPort = int( sPort )
            bValidPort = ( sPort >= 0 and sPort <= 65535 )
        except:
            bValidPort = False
        if( not bValidPort ):
            raise Exception( str(sPort) + " is not a valid port number to use to send e-mail. It must be an integer between 0 and 65535. Please check that the port parameter of the box is correct." )

        try:
           self.mail(sEmailUser,
            aTo,
            sSubject,
            sText,
            sAttachedFilePath,
            sPwd,
            sSmtp,
            sPort)
        except smtplib.SMTPAuthenticationError as e:
            raise(Exception("Authentication error, server answered : [%s] %s" % (e.smtp_code, e.smtp_error)))


        print "email sent"

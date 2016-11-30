#! /usr/bin/env python
#coding: utf-8
  


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.image import MIMEImage
import smtplib
from email import Utils
import time

def SendHtmlEmail(sender, receiver, subject, content, ctype="html", pics=[], smtpserver='mail.51ping.com', username=None, password=None):
#def SendHtmlEmail(sender, receiver, subject, content, ctype="html", pics=[], smtpserver='smtp.gmail.com', username="mavenlucky@gmail.com", password="zw19891225"):
    """subject and body are unicode objects"""
    if(ctype == "html"):
        msg = MIMEText(content, 'html', 'utf-8')
    else:
        msg = MIMEText(content, 'plain', 'utf-8')

    if(len(pics) != 0):
        msgRoot = MIMEMultipart('related')
        msgText = MIMEText(content, 'html', 'utf-8')
        msgRoot.attach(msgText)
        i = 1
        for pic in pics:
            fp = open(pic, "rb")
            image = MIMEImage(fp.read())
            fp.close()
            image.add_header('Content-ID','<img%02d>' % i)
            msgRoot.attach(image)
            i += 1
        msg = msgRoot

    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = sender
    msg['To'] = ','.join(receiver)
    msg['Message-ID'] = Utils.make_msgid()
    msg['date']=time.strftime('%a, %d %b %Y %H:%M:%S %z')
    #print receiver

    smtp = smtplib.SMTP()
    #smtp.set_debuglevel(1)
    smtp.connect(smtpserver, 25)
    #smtp.starttls()
    if username:
        smtp.login(username,password)
    #print msg.as_string()
    smtp.sendmail(sender, receiver, msg.as_string())
    #smtp.sendmail(sender, receiver, 'Date: Wed, 6 Nov 2013 06:37:46 +0000\n' + msg.as_string())
    print "send email " + subject + "succesfull. ^-^"
    smtp.quit()

## test
if __name__ == '__main__':
    data = """
        <img src="cid:img01"/>
        """
    pics=["/var/www/html/test/1.png"]
    h = """<div><font size="3">首屏数据对比</font><br><table border="1" cellspacing="0" style="font-size:2"><tbody><tr><td nowrap="" align="center" rowspan="2" colspan="1" bgcolor="#B3B3B3"><font size="2" color="#000000"></font></td>
    <td nowrap="" align="center" rowspan="1" colspan="2" bgcolor="#B3B3B3"><font size="2" color="#000000">点评首页</font></td>
    <td nowrap="" align="center" rowspan="1" colspan="2" bgcolor="#B3B3B3"><font size="2" color="#000000">美团首页</font></td>
    <td nowrap="" align="center" rowspan="1" colspan="2" bgcolor="#B3B3B3"><font size="2" color="#000000">点评详情页</font></td>
    <td nowrap="" align="center" rowspan="1" colspan="2" bgcolor="#B3B3B3"><font size="2" color="#000000">美团详情页</font></td>
    </tr>
    <tr>
    <td nowrap="" align="center" rowspan="1" colspan="1" bgcolor="#FFFFFF"><font size="2" color="#FF0000">0.858</font></td>
    <td nowrap="" align="center" rowspan="1" colspan="1" bgcolor="#FFFFFF"><font size="2" color="#000000">100</font></td>
    <td nowrap="" align="center" rowspan="1" colspan="1" bgcolor="#FFFFFF"><font size="2" color="#000000">0.838</font></td>
    <td nowrap="" align="center" rowspan="1" colspan="1" bgcolor="#FFFFFF"><font size="2" color="#000000">100</font></td>
    <td nowrap="" align="center" rowspan="1" colspan="1" bgcolor="#FFFFFF"><font size="2" color="#000000">0.846</font></td>
    <td nowrap="" align="center" rowspan="1" colspan="1" bgcolor="#FFFFFF"><font size="2" color="#000000">100</font></td>
    <td nowrap="" align="center" rowspan="1" colspan="1" bgcolor="#FFFFFF"><font size="2" color="#000000">1.03</font></td>
    <td nowrap="" align="center" rowspan="1" colspan="1" bgcolor="#FFFFFF"><font size="2" color="#000000">100</font></td>
    </tr>
    </tbody></table></div>"""
    #SendHtmlEmail("hello@51ping.com", "weiwei.zeng@dianping.com", "pmail", data, pics=pics)
    SendHtmlEmail("hello@51ping.com", ["weiwei.zeng@dianping.com"], "ceshi", 'hehe')

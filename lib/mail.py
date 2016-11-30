#!/bin/env python
# encoding=utf-8

__author__ = 'xiangfeng'

import os
import re
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header
import email
import datetime
from bs4 import BeautifulSoup
import requests
from flask import current_app
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from extensions import db


class MailManage():
    def __init__(self):
        pass

    @staticmethod
    def save_file(filename, data, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            filepath = os.sep.join([path, filename])
            f = open(filepath, 'wb')
            f.write(data)
            f.close()
        except Exception as e:
            print str(e)
            if f:
                f.close()

    #字符编码转换方法
    @staticmethod
    def my_unicode(s, encoding):
        if encoding:
            try:
                return unicode(s, encoding)
            except Exception as e:
                current_app.logger.info(str(e))
                return unicode(s, 'gbk')
        else:
            return unicode(s)

    def parse_email(self, msg, mypath):
        mail_content = None
        contenttype = None
        suffix = None
        fnames = list()
        for part in msg.walk():
            if not part.is_multipart():
                contenttype = part.get_content_type()
                filename = part.get_filename()
                charset = part.get_charset()
                if filename:
                    h = email.Header.Header(filename)
                    dh = email.Header.decode_header(h)
                    fname = dh[0][0]
                    encode_str = dh[0][1]
                    if encode_str is not None:
                        if charset is None:
                            fname = fname.decode(encode_str, 'gbk')
                        else:
                            fname = fname.decode(encode_str, 'ascii')
                    data = part.get_payload(decode=True)
                    if fname is not None or fname != '':
                        fnames.append(fname)
                        self.save_file(fname, data, mypath)
                else:
                    if contenttype in ['text/plain']:
                        suffix = '.txt'
                    if contenttype in ['text/html']:
                        suffix = '.htm'
                    if charset is None:
                        try:
                            mail_content = part.get_payload(decode=True).decode('gbk')
                        except Exception as e:
                            try:
                                mail_content = part.get_payload(decode=True).decode('utf-8')
                            except Exception as e1:
                                current_app.logger.error(str(e1))
                        # mail_content = part.get_payload(decode=True).decode('gb2312')
                    else:
                        mail_content = part.get_payload(decode=True).decode(charset)
        return mail_content, suffix, fnames

    # def parse_user(self, users_str):
    #     users = list()
    #     if users_str:
    #         users_tmp = users_str.split(',')
    #         for user in users_tmp:
    #             try:
    #                 user_tmp = user.strip()
    #                 index1 = user_tmp.find('=?')
    #                 index2 = user_tmp.find('?=')
    #                 user_tmp_reversed = user_tmp[::-1]
    #                 index3 = user_tmp_reversed.find('>')
    #                 index4 = user_tmp_reversed.find('<')
    #                 parse_user = user_tmp_reversed[index3:index4+1][::-1]
    #                 if index1 != -1 and index2 != -1:
    #                     alias_name = email.Header.decode_header(user_tmp[index1:index2+2])
    #                 else:
    #                     alias_name = email.Header.decode_header(user_tmp.replace(parse_user, ''))
    #                 users.append(self.my_unicode(alias_name[0][0], alias_name[0][1]) + parse_user)
    #             except Exception as e:
    #                 current_app.logger.error(str(e))
    #                 users.append(user)
    #     return users

    def parse_user(self, users_str):
        users = list()
        if users_str:
            users_tmp = users_str.split(',')
            for user in users_tmp:
                try:
                    name, addr = email.utils.parseaddr(user)
                    alias_name = email.Header.decode_header(name)
                    users.append(self.my_unicode(alias_name[0][0], alias_name[0][1]) + '<' + addr + '>')
                except Exception as e:
                    current_app.logger.error(str(e))
                    users.append(user)
        return users

    @staticmethod
    def parse_mail_user(user_string):
        """
        parsing user and mail from user_string,
        for example: aaaa<xxxx@dianping.com> --> aaaa, xxxx and <xxxx@dianping.com>
        :param user_string:
        :return: user, account, mail
        """
        p = re.compile(r'<[.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[.a-zA-Z0-9_-]+>)')
        user_tmp = p.search(user_string)
        if user_tmp:
            user_mail = user_tmp.group()
            user = user_string[:user_string.find(user_mail)]
            tmp = user_mail.split('@')
            if tmp:
                account = tmp[0][1:]
            else:
                account = user
        else:
            user = account = user_string
            user_mail = user_string
        return user, account, user_mail.strip('<>')

    @staticmethod
    def validate_email(mail):
        pattern = "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$"
        if len(mail) > 7:
            if re.match(pattern, mail):
                return True
        return False

    def gen_email(self, user, email_suffix):
        if not email_suffix:
            email_suffix = 'dianping.com'
        if not self.validate_email(user):
            user = '@'.join([user, email_suffix])
        return user

    @staticmethod
    def _format_addr(strs):
        name, addr = email.utils.parseaddr(strs)
        return email.utils.formataddr((Header(name, 'utf-8').encode(), addr.encode('utf-8') if isinstance(addr, unicode) else addr))

    @staticmethod
    def _format_addr2(strs):
        name, addr = email.utils.parseaddr(strs)
        return email.utils.formataddr((Header(name, 'gb2312').encode(), addr.encode('gb2312')))

    def send_mail(self, mailhost, account, password, mail_to_list, mail_cc_list, subject, content, attachment, port=587, ssl=1):
        try:
            msg = MIMEMultipart('mixed')
            from_addr = account
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = self._format_addr(u'IT支持 <%s>' % 'itsupport@dianping.com')
            # msg['To']接收的是字符串而是list，如果有多个邮件地址，用,分隔即可
            msg['To'] = ','.join([self._format_addr(i) for i in mail_to_list])
            msg['CC'] = ','.join([self._format_addr(i) for i in mail_cc_list])
            # 添加文本内容
            try:
                html, imgs = self.handle(content)
            except Exception, e:
                current_app.logger.error(str(e))
                return False

            img_num = len(imgs)
            for i in range(img_num):
                image = MIMEImage(imgs[i])
                image.add_header('Content-ID', '<img%d>' % (i+1))
                msg.attach(image)

            htm = MIMEText(html, _subtype='html', _charset='utf-8')
            msg.attach(htm)

            # 添加附件
            for i in attachment:
                filename = os.path.basename(i)
                att = MIMEText(open(i, 'rb').read(), 'base64', 'utf-8')
                att["Content-Type"] = 'application/octet-stream'
                att["Content-Disposition"] = 'attachment; filename="%s"' % filename
                msg.attach(att)
            try:
                server = smtplib.SMTP(mailhost, 587)
                server.starttls()
                server.login(account, password)
                server.sendmail(from_addr, mail_to_list + mail_cc_list, msg.as_string())
                server.quit()
                return True
            except Exception as e:
                print str(e)
                return False
        except Exception as e:
            print str(e)
            return False

    # def get_mail(self, mailhost, account, password, mypath, port=143, ssl=1):
    #     mails_info = list()
    #     if ssl == 1:
    #         imapServer = imaplib.IMAP4_SSL(mailhost, port)
    #     else:
    #         imapServer = imaplib.IMAP4(mailhost, port)
    #     imapServer.login(account, password)
    #     imapServer.select()
    #     #Message statues = 'All,Unseen,Seen,Recent,Answered, Flagged'
    #     resp, items = imapServer.search(None, 'Unseen')
    #     for i in items[0].split():
    #         resp, mail_data = imapServer.fetch(i, "(RFC822)")
    #         mail_text = mail_data[0][1]
    #         msg = email.message_from_string(mail_text)
    #         print 'msg["From"]:', msg["From"]
    #         raw_from = msg["From"].split(' ')
    #         print 'raw_from:', raw_from
    #         if len(raw_from) == 2:
    #             print 'raw_from[0]:', raw_from[0]
    #             from_name = email.Header.decode_header((raw_from[0]).strip('\"'))
    #             print 'from_name:', from_name
    #             str_from = self.my_unicode(from_name[0][0], from_name[0][1]) + raw_from[1]
    #             print 'str_from:', str_from
    #         else:
    #             str_from = msg["From"]
    #         mail_from = self.parse_user(msg['From'])
    #         str_to = self.parse_user(msg["To"])
    #         str_cc = self.parse_user(msg["CC"])
    #         try:
    #             if '-' in msg['Date']:
    #                 strdate = msg["Date"].split(',')[1].split('-')[0].strip()
    #             else:
    #                 strdate = msg["Date"].split(',')[1].split('+')[0].strip()
    #             str_date = datetime.datetime.strptime(strdate, '%d %b %Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    #         except Exception as e:
    #             print str(e)
    #             str_date = msg["Date"]
    #         print 'msg["Subject"]:', msg["Subject"]
    #         subject = email.Header.decode_header(msg["Subject"])
    #
    #         print subject
    #         str_subject = self.my_unicode(subject[0][0], subject[0][1])
    #         print subject
    #         try:
    #             mail_content, suffix, fnames = self.parse_email(msg, os.sep.join([mypath, i]))
    #         except Exception as e:
    #             print str(e)
    #         if suffix is not None and suffix != '' and mail_content is not None and mail_content != '':
    #             self.save_file(str(i) + suffix, mail_content, mypath)
    #         # typ, response = imapServer.store(i, '+FLAGS', r'(\Deleted)')
    #         mail_info = dict()
    #         mail_info['send_time'] = str_date
    #         mail_info['c_from'] = str_from
    #         mail_info['to'] = ';'.join(str_to)
    #         mail_info['cc'] = ';'.join(str_cc)
    #         mail_info['details'] = mail_content
    #
    #         fnames_length = len(fnames)
    #         if fnames:
    #             for num in xrange(fnames_length):
    #                 fnames[num] = os.sep.join([mypath, i, fnames[num]])
    #         mail_info['attachment'] = fnames
    #
    #         mail_info['m_class'] = 'EMAIL'
    #         mail_info['subject'] = str_subject
    #         mail_info['mail_number'] = int(i)
    #         mails_info.append(mail_info)
    #     imapServer.close()
    #     imapServer.logout()
    #     return mails_info

    def get_mail(self, mailhost, account, password, mypath, port=143, ssl=1):
        mails_info = list()
        if ssl == 1:
            imapServer = imaplib.IMAP4_SSL(mailhost, port)
        else:
            imapServer = imaplib.IMAP4(mailhost, port)
        imapServer.login(account, password)
        imapServer.select()
        #Message statues = 'All,Unseen,Seen,Recent,Answered, Flagged'
        resp, items = imapServer.search(None, 'Unseen')
        for i in items[0].split():
            resp, mail_data = imapServer.fetch(i, "(RFC822)")
            mail_text = mail_data[0][1]
            msg = email.message_from_string(mail_text)
            # raw_from = msg["From"].split(' ')
            # if len(raw_from) == 2:
            #     from_name = email.Header.decode_header((raw_from[0]).strip('\"'))
            #     str_from = self.my_unicode(from_name[0][0], from_name[0][1]) + raw_from[1]
            # else:
            #     str_from = msg["From"]
            str_from = self.parse_user(msg['From'])
            str_to = self.parse_user(msg["To"])
            str_cc = self.parse_user(msg["CC"])
            try:
                if '-' in msg['Date']:
                    strdate = msg["Date"].split(',')[1].split('-')[0].strip()
                else:
                    strdate = msg["Date"].split(',')[1].split('+')[0].strip()
                str_date = datetime.datetime.strptime(strdate, '%d %b %Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print str(e)
                str_date = msg["Date"]
            subject = email.Header.decode_header(msg["Subject"])
            str_subject = ''
            for j in subject:
                str_subject += self.my_unicode(j[0], j[1])
            try:
                mail_content, suffix, fnames = self.parse_email(msg, os.sep.join([mypath, i]))
            except Exception as e:
                mail_content = ''
                suffix = ''
                fnames = ''
                print str(e)
            if suffix is not None and suffix != '' and mail_content is not None and mail_content != '':
                self.save_file(str(i) + suffix, mail_content, mypath)
            # typ, response = imapServer.store(i, '+FLAGS', r'(\Deleted)')
            mail_info = dict()
            mail_info['send_time'] = str_date
            mail_info['c_from'] = ';'.join(str_from)
            mail_info['to'] = ';'.join(str_to)
            mail_info['cc'] = ';'.join(str_cc)
            mail_info['details'] = mail_content

            fnames_length = len(fnames)
            if fnames:
                for num in xrange(fnames_length):
                    fnames[num] = os.sep.join([mypath, i, fnames[num]])
            mail_info['attachment'] = fnames

            mail_info['m_class'] = 'EMAIL'
            mail_info['subject'] = str_subject
            mail_info['mail_number'] = int(i)
            mails_info.append(mail_info)
        imapServer.close()
        imapServer.logout()
        return mails_info

    def filter(self, mails_info):
        filter_types = self.filter_type()
        conditions = dict()
        for i in filter_types:
            conditions[i] = self.filter_conditions(i)
        try:
            for mail_info in mails_info:
                mail_info['validity'] = 'VALID'
                for i in conditions:
                    for j in conditions[i]:
                        if j['mail_head'] == 'c_from':
                            tmp_value = self.parse_mail_user(mail_info.get(j['mail_head']))[2]
                        else:
                            tmp_value = mail_info.get(j['mail_head'])
                        if j['match_type'] == 'ACCURATE':
                            if j['equal'] == 'YES':
                                if j['value'] == tmp_value:
                                    if filter_types[i] == 'YES':
                                        mail_info['validity'] = 'INVALID'
                                        break
                                else:
                                    if filter_types[i] == 'NO':
                                        mail_info['validity'] = 'INVALID'
                                        break
                            elif j['equal'] == 'NO':
                                if j['value'] != tmp_value:
                                    if filter_types[i] == 'YES':
                                        mail_info['validity'] = 'INVALID'
                                        break
                                else:
                                    if filter_types[i] == 'NO':
                                        mail_info['validity'] = 'INVALID'
                                        break
                        elif j['match_type'] == 'APPROXIMATE':
                            if j['equal'] == 'YES':
                                if j['value'] in tmp_value:
                                    if filter_types[i] == 'YES':
                                        mail_info['validity'] = 'INVALID'
                                        break
                                else:
                                    if filter_types[i] == 'NO':
                                        mail_info['validity'] = 'INVALID'
                                        break
                            elif j['equal'] == 'NO':
                                if j['value'] not in tmp_value:
                                    if filter_types[i] == 'YES':
                                        mail_info['validity'] = 'INVALID'
                                        break
                                else:
                                    if filter_types[i] == 'NO':
                                        mail_info['validity'] = 'INVALID'
                                        break
                    if mail_info['validity'] == 'INVALID':
                        break
            return mails_info
        except Exception as e:
            print str(e)
            return []

    @staticmethod
    def handle(html):
        soup = BeautifulSoup(html, "html.parser")
        imgs = soup.findAll('img')
        img_datas = []
        cid = 1
        for img in imgs:
            src = img.get('src')
            if src.startswith('data:image/png;base64,'):
                content = src.split(',', 1)[1].decode('base64')
            elif src.startswith('http:') or src.startswith('https:'):
                try:
                    content = requests.get(src).content
                except Exception:
                    continue
            elif src.startswith('/'):
                try:
                    path = '.%s' % src
                    with open(path, 'r') as f:
                        content = f.read()
                except Exception:
                    continue
            else:
                continue
            img_datas.append(content)
            img['src'] = "cid:img%d" % cid
            cid += 1
        return str(soup), img_datas

    @staticmethod
    def handle_details(html, attachment):
        try:
            soup = BeautifulSoup(html, "html.parser")
            imgs = soup.findAll('img')
            attachment = attachment.split(';')
            num = 0
            for img in imgs:
                src = img.get('src')
                if src.startswith('cid:'):
                    html = html.replace(src, '/%s' % attachment[num])
                num += 1
        except Exception as e:
            print str(e)
        return html


def parse_user(self, users_str):
    users = list()
    if users_str:
        users_tmp = users_str.split(',')
        for user in users_tmp:
            try:
                user_tmp = user.strip()
                index1 = user_tmp.find('=?')
                index2 = user_tmp.find('?=')
                user_tmp_reversed = user_tmp[::-1]
                index3 = user_tmp_reversed.find('>')
                index4 = user_tmp_reversed.find('<')
                parse_user = user_tmp_reversed[index3:index4+1][::-1]
                if index1 != -1 and index2 != -1:
                    alias_name = email.Header.decode_header(user_tmp[index1:index2+2])
                else:
                    alias_name = email.Header.decode_header(user_tmp.replace(parse_user, ''))
                users.append(self.my_unicode(alias_name[0][0], alias_name[0][1]) + parse_user)
            except Exception as e:
                current_app.logger.error(str(e))
                users.append(user)
    return users

# def my_unicode(s, encoding):
#     if encoding:
#         return unicode(s, encoding)
#     else:
#         return unicode(s)
#
#
# def parse_user(users_str):
#     users = list()
#     if users_str:
#         users_tmp = users_str.split(',')
#         for user in users_tmp:
#             try:
#                 name, addr = email.utils.parseaddr(user)
#                 alias_name = email.Header.decode_header(name)
#                 users.append(my_unicode(alias_name[0][0], alias_name[0][1]) + '<' + addr + '>')
#             except Exception as e:
#                 current_app.logger.error(str(e))
#                 users.append(user)
#     return users


def parse_email(msg):
    mail_content = None
    contenttype = None
    suffix = None
    fnames = list()
    for part in msg.walk():
        if not part.is_multipart():
            contenttype = part.get_content_type()
            filename = part.get_filename()
            charset = part.get_charset()
            if filename:
                h = email.Header.Header(filename)
                dh = email.Header.decode_header(h)
                fname = dh[0][0]
                encode_str = dh[0][1]
                if encode_str is not None:
                    if charset is None:
                        fname = fname.decode(encode_str, 'gbk')
                    else:
                        fname = fname.decode(encode_str, 'ascii')
                data = part.get_payload(decode=True)

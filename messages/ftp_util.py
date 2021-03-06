__author__ = 'cysnake4713'


# -*- coding: utf-8 -*-
import ftplib
import hashlib
import random
import simplejson
import os
import time

import ftputil


class MySession(ftplib.FTP):
    def __init__(self, host, userid, password, port):
        """Act like ftplib.FTP's constructor but connect to another port."""
        ftplib.FTP.__init__(self)
        self.connect(host, port)
        self.login(userid, password)


class InternalHome():
    _cp_path = "/web/clupload"
    _FTP_ADDRESS = 'ftp.updis.cn'
    _FTP_PORT = 2121
    _FTP_USER_NAME = 'ftpuser'
    _FTP_PASSWORD = 'updis_ftp_2013'

    def _get_salt(self, current_time, filename):
        salt = str(random.random())
        h = hashlib.md5(current_time + salt).hexdigest()
        return h

    def _generate_file_name(self, s_file_name):


        current_time = time.strftime('%Y-%m-%d_%H-%M', time.localtime(time.time()))
        salt = self._get_salt(current_time, s_file_name)
        return '%s_%s%s' % (current_time, salt, os.path.splitext(s_file_name)[1])


    def _upload_file_ftp(self, file_data, file_name):
        if os.getenv("HOME"):
            HOME = os.getenv("HOME") + '/tempfile'
        else:
            HOME = '/home/updisadmin' + '/tempfile'
        if not os.path.exists(HOME):
            os.mkdir(HOME)
        new_file_name = self._generate_file_name(file_name)
        output = open(HOME + '/' + new_file_name, 'wb')
        output.write(file_data)
        output.close()
        host = None
        try:
            host = ftputil.FTPHost(self._FTP_ADDRESS, self._FTP_USER_NAME, self._FTP_PASSWORD, port=self._FTP_PORT,
                                   session_factory=MySession)
            host.upload(HOME + '/' + str(new_file_name), '/erpupload/' + str(new_file_name))
            args = {
                'filename': new_file_name,
                'success': True,
            }
        except Exception, e:
            args = {'error': e.message, 'filename': file_name}
        finally:
            if host:
                host.close()
            if os.path.isfile(HOME + '/' + new_file_name):
                os.remove(HOME + '/' + new_file_name)
            return args

    def _create_attachment(self, req, qqfile, resize_image=False):
        # context = req.context
        # Model = req.session.model('ir.attachment')

        # datas = base64.encodestring(req.httprequest.data)
        # if resize_image:
        #     datas = tools.image_resize_image(datas, size=(700, 700))

        args = self._upload_file_ftp(req.httprequest.data, qqfile)

        # attachment_id = Model.create({
        #                                  'name': qqfile,
        #                                  'datas': datas,
        #                                  'datas_fname': qqfile,
        #                              }, context)
        return args
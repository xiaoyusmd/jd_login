# -*- coding:utf-8 -*-

import time
import requests
from bs4 import BeautifulSoup


class JD_crawl:
    def __init__(self, username, password):
        self.headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'
                                      ' (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
                        'Referer': 'https://www.jd.com/',
                        }
        self.login_url = "https://passport.jd.com/new/login.aspx"
        self.post_url = "https://passport.jd.com/uc/loginService"
        self.auth_url = "https://passport.jd.com/uc/showAuthCode"
        self.session = requests.session()
        self.username = username
        self.password = password

    def get_login_info(self):
        html = self.session.get(self.login_url, headers=self.headers).content
        soup = BeautifulSoup(html, 'lxml')

        uuid = soup.select('#uuid')[0].get('value')
        eid = soup.select('#eid')[0].get('value')
        fp = soup.select('input[name="fp"]')[0].get('value')  # session id
        _t = soup.select('input[name="_t"]')[0].get('value')  # token
        login_type = soup.select('input[name="loginType"]')[0].get('value')
        pub_key = soup.select('input[name="pubKey"]')[0].get('value')
        sa_token = soup.select('input[name="sa_token"]')[0].get('value')

        auth_page = self.session.post(self.auth_url,
                                      data={'loginName': self.username, 'nloginpwd': self.password}).text
        if 'true' in auth_page:
            auth_code_url = soup.select('#JD_Verification1')[0].get('src2')
            auth_code = str(self.get_auth_img(auth_code_url))
        else:
            auth_code = ''

        data = {
            'uuid': uuid,
            'eid': eid,
            'fp': fp,
            '_t': _t,
            'loginType': login_type,
            'loginname': self.username,
            'nloginpwd': self.password,
            'chkRememberMe': True,
            'pubKey': pub_key,
            'sa_token': sa_token,
            'authcode': auth_code
            }
        return data

    def get_auth_img(self, url):
        auth_code_url = 'http:{}&yys={}'.format(url, str(int(time.time()*1000)))
        auth_img = self.session.get(auth_code_url, headers=self.headers)
        with open('authcode.jpg', 'wb') as f:
            f.write(auth_img.content)
        code_typein = input('请根据下载图片输入验证码：')
        return code_typein

    def login(self):
        data = self.get_login_info()
        headers = {
                    'Referer': self.post_url,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'
                                  ' (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'
                  }
        try:
            login_page = self.session.post(self.post_url, data=data, headers=headers)
            print(login_page.text)
        except Exception as e:
            print(e)

        # self.session.cookies.clear()

    def shopping(self):
        login = self.session.post('https://cart.jd.com/cart.action', headers=self.headers)
        print(login.text)


if __name__ == '__main__':
    un = input('请输入京东账号：')
    pwd = input('请输入京东密码：')
    jd = JD_crawl(un, pwd)
    jd.login()
    jd.shopping()
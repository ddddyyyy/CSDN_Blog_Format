import json
import logging
import logging.handlers
import os
import re
import time
import urllib.request

from lxml import etree
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


def save_cookies(cookies):
    jsonCookies = json.dumps(cookies)
    with open('cookies.json', 'w') as f:
        f.write(jsonCookies)


# 删除字典数组重复的元素
def delete_duplicate(li):
    temp_list = list(set([str(i) for i in li]))
    li = [eval(i) for i in temp_list]
    return li


class CSDN:
    def __init__(self):
        # 输出文件的目录
        self.output = '/root/Hexo/source/_posts/'

        # 创建Logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        # 创建Handler

        # 终端Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        # 添加到Logger中
        self.logger.addHandler(console_handler)

        self.url = 'https://passport.csdn.net/login'

        self.driver = None
        self.account = ''
        self.password = ''
        self.username = ''
        self.usertoken = ''
        self.userinfo = ''
        self.header = [('Cookie', 'UserName=%s;UserInfo=%s;UserToken=%s;')]
        self.blog_url = ''

    def init_header(self):
        self.get_cookies()
        self.blog_url = 'https://blog.csdn.net/{0}/article/list/'.format(self.username)
        self.header = [
            ('Cookie', 'UserName=%s;UserInfo=%s;UserToken=%s;' % (self.username, self.userinfo, self.usertoken))]
        # 装载cookie
        opener = urllib.request.build_opener()
        opener.addheaders = self.header
        urllib.request.install_opener(opener)
        print(self.header)

    def get_cookies(self):
        with open('cookies.json', 'r', encoding='utf-8') as f:
            list_cookies = json.loads(f.read())
        for cookie in list_cookies:
            if str(cookie['name']) == 'UserName':
                self.username = cookie['value']
            if str(cookie['name']) == 'UserInfo':
                self.userinfo = cookie['value']
            if str(cookie['name']) == 'UserToken':
                self.usertoken = cookie['value']

    def input(self):
        self.account = input("account:")
        self.password = input("password:")

    def login(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--no-sandbox")
        # windows
        # chrome_options.binary_location = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        # driver = webdriver.Chrome(chrome_options=chrome_options)
        # linux
        chrome_options.binary_location = '/opt/google/chrome/chrome'
        driver = webdriver.Chrome(executable_path='/opt/google/chrome/chromedriver', chrome_options=chrome_options)
        # mac
        # chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        # driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options)
        try:
            print('请输入账号密码')
            self.input()
            print('正在加载页面。。。。。')
            driver.get(self.url)
            # 跳转到账号登录界面
            driver.find_element_by_xpath('//*[@id="app"]/div/div/div/div[2]/div[2]/ul/li[1]/a').click()
            account = driver.find_element_by_xpath('//*[@id="all"]')
            password = driver.find_element_by_xpath('//*[@id="password-number"]')
            while True:
                account.clear()
                account.send_keys(self.account)
                password.clear()
                password.send_keys(self.password)
                driver.find_element_by_xpath(
                    '//*[@id="app"]/div/div/div/div[2]/div[2]/form/div/div[6]/div/button').click()
                time.sleep(3)
                try:
                    error = driver.find_element_by_xpath('//*[@id="js_err_dom"]')
                except NoSuchElementException:
                    print('登录成功')
                    save_cookies(driver.get_cookies())
                    break
                if error is not None:
                    print(error.text)
                    print('请重新输入账号密码')
                    self.input()
        except Exception as e:
            self.logger.exception(e)
        finally:
            driver.quit()
        self.init_header()

    def get_article_list(self):
        # 最终所有文章id和日期的数组
        result_list = []

        # 获得文章链接，由于页面有一些评论的链接，需要过滤掉
        r_str = '^https\:\/\/blog\.csdn\.net\/{0}\/article\/details\/[0-9]+$'.format(self.username)
        url_re = re.compile(r_str)
        # 替换url得到文章的id
        replace_re = re.compile('^https\:\/\/blog\.csdn\.net\/.+\/article\/details\/')

        j = 1
        # 这里直接使用循环代替页码的获取了，当检索不到数据的时候跳出循环
        while True:
            r = urllib.request.urlopen(self.blog_url + str(j))
            html = etree.HTML(r.read())

            # 获得所有的链接
            u_list = html.xpath('//*[@id="mainBox"]/main//a[@href]')
            id_list = []
            for uri in u_list:
                ri = url_re.match(uri.attrib['href'])
                if ri is not None:
                    # 获取文章id
                    data = uri.getparent().getparent().xpath('div[1]/p[1]/span')[0].text
                    id_list.append({'id': replace_re.sub('', uri.attrib['href']), 'data': data})
            temp_list = delete_duplicate(id_list)
            # temp_list = id_list
            if len(temp_list) == 0:
                self.logger.info('结束')
                break
            j += 1
            result_list += temp_list

        self.logger.info(len(result_list))

        for i in result_list:
            try:
                if not self.format_article(i):
                    self.format_article(i)
            except Exception as a:
                self.logger.error(a)

    # 得到文章的markdown
    def format_article(self, dic):
        html = urllib.request.urlopen('https://mp.csdn.net/mdeditor/getArticle?id={0}'.format(dic['id'])).read()
        j = json.loads(html)
        if not j['status']:
            # 获取网页失败
            self.logger.error('cookie过期')
            self.logger.error(j)
            self.login()
            return False
        title = j['data']['title']
        markdowncontent = j['data']['markdowncontent']
        categories = j['data']['categories']
        c_list = categories.split(',')
        c_str = ""
        for i in c_list:
            c_str += "  - [{0}]\n".format(i)
        tags = j['data']['tags']
        # 得到Hexo的所需的markdown格式
        string = "---\ntitle: {0}\ndate: {3}\ntags: [{1}]\ncategories:\n{2}\n\n---\n\n<!--more-->\n\n\n\n"
        string = string.format(title, tags, c_str, dic['data'])
        result = string + markdowncontent
        file = open(self.output + '{0}.md'.format(title), 'w')
        file.write(result)
        file.close()
        self.logger.info(self.output + '{0}.md'.format(title) + '添加成功！')
        return True

    def run(self):
        try:
            self.get_article_list()
        except Exception as a:
            self.logger.error(a)


if __name__ == '__main__':
    csdn = CSDN()
    if not os.path.exists('cookies.json'):
        csdn.login()
    csdn.init_header()
    csdn.run()


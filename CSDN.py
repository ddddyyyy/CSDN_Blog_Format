import argparse
import json
import logging
import logging.handlers
import os
import re
import urllib.request

from lxml import etree


# 删除字典数组重复的元素
def delete_duplicate(li):
    temp_list = list(set([str(i) for i in li]))
    li = [eval(i) for i in temp_list]
    return li


class CSDN:
    def __init__(self):
        # 输出文件的目录
        self.output = ''
        # 自己的名字
        self.user = 'madonghyu'

        self.blog_url = 'https://blog.csdn.net/{0}/article/list/'.format(self.user)

        self.header = [
            ('Cookie', '')]

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
        # 装载cookie
        opener = urllib.request.build_opener()
        opener.addheaders = self.header
        urllib.request.install_opener(opener)

    # 初始化请求header
    def init_header(self, cookie):
        # header = [
        #     ('Cookie', 'UserToken={0};UserInfo={0}'.format(cookie))]
        header = [('Cookie', 'UserName={0};UserInfo={1}; UserToken={1}'.format(self.user, cookie))]
        # 装载cookie
        opener = urllib.request.build_opener()
        opener.addheaders = header
        urllib.request.install_opener(opener)

    def get_article_list(self):
        # 最终所有文章id和日期的数组
        result_list = []

        # 获得文章链接，由于页面有一些评论的链接，需要过滤掉
        r_str = '^https\:\/\/blog\.csdn\.net\/{0}\/article\/details\/[0-9]+$'.format(self.user)
        url_re = re.compile(r_str)
        # 替换url得到文章的id
        replace_re = re.compile('^https://blog\.csdn\.net/.+/article/details/')

        j = 1
        self.logger.info('开始获取文章总数目')
        # 这里直接使用循环代替页码的获取了，当检索不到数据的时候跳出循环
        while True:
            r = urllib.request.urlopen(self.blog_url + str(j))
            html = etree.HTML(r.read())

            # 获得所有的链接
            u_list = html.xpath('//*[@id="mainBox"]/main//a[@href]')
            id_list = []
            for uri in u_list:
                # '//*[@id="mainBox"]/main/div[2]/div[2]/h4/a'
                # '//*[@id="mainBox"]/main/div[2]/div[2]/div[1]/p[1]/span'
                ri = url_re.match(uri.attrib['href'])

                if ri is not None:
                    # 获取文章id
                    data = uri.getparent().getparent().xpath('div[1]/p[1]/span')[0].text
                    id_list.append({'id': replace_re.sub('', uri.attrib['href']), 'data': data})
            temp_list = delete_duplicate(id_list)
            # temp_list = id_list
            if len(temp_list) == 0:
                break
            j += 1
            result_list += temp_list

        self.logger.info('总共有%d篇文章' % len(result_list))

        for i in result_list:
            try:
                self.format_article(i)
            except Exception as a:
                self.logger.error(a)

    # 得到文章的markdown
    def format_article(self, dic):
        html = urllib.request.urlopen('https://mp.csdn.net/mdeditor/getArticle?id={0}'.format(dic['id'])).read()
        j = json.loads(html)
        if not j['status']:
            self.logger.error('cookie过期')
            self.logger.error(j)
            return
        title = j['data']['title']
        markdowncontent = j['data']['markdowncontent']
        categories = j['data']['categories']
        c_list = categories.split(',')
        c_str = ""
        for i in c_list:
            c_str += "  - [{0}]\n".format(i)
        tags = j['data']['tags']
        # 得到Hexo的所需的markdown格式
        string = "---\ntitle: {0}\ndate: {3}\ntags: [{1}]\ncategories:\n{2}\n\n---\n\n<!--more-->\n\n\n\n" \
            .format(title,
                    tags,
                    c_str,
                    dic['data'])
        if self.output[-1] is not '/':
            self.output += '/'
        # 创建文件夹
        if not os.path.exists(self.output):
            os.mkdir(self.output)
        result = string + markdowncontent
        with open(self.output + '{0}.md'.format(title), 'w') as file:
            file.write(result)
            self.logger.info(title + '添加成功！')

    def run(self):
        try:
            self.get_article_list()
        except Exception as a:
            self.logger.error(a)


# 如果觉得每次启动脚本都要输入参数很麻烦，可以直接将下面的代码注释取消，完善csdn.output，csdn.user，csdn.init_header的值既可

# if __name__ == '__main__':
#     csdn = CSDN()
#
#     # 输出路径
#     csdn.output = './output/'
#     # 输入自己的CSDN账户名
#     csdn.user = ''
#     # CSDN的登录之后的cookie,即UserToken和UserInfo的值，这两个的值都是一样的
#     # 可以在CSDN的网站下打开浏览器的开发者模式，访问自己的文章页面，查看请求的header得到
#     csdn.init_header('')
#
#     csdn.run()


# 控制台参数输入
parser = argparse.ArgumentParser()

# 添加参数
parser.add_argument('-o', metavar='文章输出路径', type=str, required=False, default='./output/')
parser.add_argument('-u', metavar='自己的CSDN账户名', type=str, required=True)
parser.add_argument('-c', metavar='CSDN的登录之后的cookie{UserToken和UserInfo}', type=str, required=True,
                    help='可以在CSDN的网站下打开浏览器的开发者模式，'
                         '访问自己的文章页面，查看请求的header得到。字符串不能存在空格！')

try:
    # 参数解析
    args = parser.parse_args()
    csdn = CSDN()
    csdn.output = args.o
    csdn.user = args.u
    csdn.init_header(args.c)
    csdn.run()

except argparse.ArgumentError:
    parser.print_help()

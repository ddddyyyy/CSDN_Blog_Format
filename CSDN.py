import argparse
import json
import logging
import logging.handlers
import math
import os
import urllib.request


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

        # 得到所有文章列表的url
        self.article_list_url = 'https://blog.csdn.net/{0}/phoenix/article/list/'.format(self.user)

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
        i = 1
        page_num = 0
        lists = []
        # 循环遍历
        while True:
            response = json.loads(urllib.request.urlopen(self.article_list_url + str(i)).read())
            if response['status'] is 1:
                if page_num == 0:
                    # 得到遍历的次数
                    page_num = math.ceil(response['data']['total'] / 20)
                # 得到文章列表
                article_list = response['data']['article_list']
                for data in article_list:
                    # 得到文章的id和创建日期
                    lists.append({'id': data['ArticleId'], 'data': data['PostTime']})
            if i > page_num:
                break
            i = i + 1
        for l in lists:
            try:
                self.format_article(l)
            except Exception as a:
                self.logger.error(a)

    # 得到文章的markdown
    def format_article(self, dic):
        html = urllib.request.urlopen('https://blog-console-api.csdn.net/v1/editor/getArticle?id={0}'.format(dic['id'])).read()
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

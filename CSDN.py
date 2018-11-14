import json
import logging
import logging.handlers
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
        self.output = '/root/Hexo/source/_posts/'
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

    def get_article_list(self):
        # 最终所有文章id和日期的数组
        result_list = []

        # 获得文章链接，由于页面有一些评论的链接，需要过滤掉
        r_str = '^https\:\/\/blog\.csdn\.net\/{0}\/article\/details\/[0-9]+$'.format(self.user)
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
                self.logger.info('结束')
                break
            j += 1
            result_list += temp_list

        self.logger.info(len(result_list))

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
        string = "---\ntitle: {0}\ndate: {3}\ntags: [{1}]\ncategories:\n{2}\n\n---\n\n<!--more-->\n\n\n\n".format(title,
                                                                                                                  tags,
                                                                                                                  c_str,
                                                                                                                  dic[
                                                                                                                      'data'])
        result = string + markdowncontent
        file = open(self.output + '{0}.md'.format(title), 'w')
        file.write(result)
        file.close()
        self.logger.info(self.output + '{0}.md'.format(title) + '添加成功！')

    def run(self):
        try:
            self.get_article_list()
        except Exception as a:
            self.logger.error(a)


if __name__ == '__main__':
    csdn = CSDN()
    csdn.run()
    # 输出路径
    # csdn.output = './'
    # 输入自己的CSDN账户名
    # csdn.user = ''
    # 自己的登录之后的cookie
    # csdn.header = [('Cookie', yourcookie)]

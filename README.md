# CSDN_Blog_Format
---
将自己CSDN的文章转化为Hexo里面的markdown格式
---
运行次脚本的环境：
1. python3.x
2. 所需python库:lxml,logger
---
使用方法其一，直接在修改代码

1. 找到注释掉的代码，将注释去掉
2. 设置输出路径
 - csdn.output = './'
3. 设置自己的CSDN账户名
 - csdn.user = ''
4. 设置自己的登录之后的cookie，可以自己点击一篇自己的文章编辑查看url的header得到，找到UserToken和UserInfo其中一个的值，这两个的值都是一样的
 - csdn.init_header('')
5. 运行脚本
---

使用方法其二，运行命令行

CSDN.py [-h] [-o 文章输出路径] -u 自己的CSDN账户名 -c  CSDN的登录之后的cookie{UserToken和UserInfo}

---
使用方法其三
如果不想要设置cookie，可以查看该项目的分支https://github.com/ddddyyyy/CSDN_Blog_Format/tree/login
可以通过使用账号密码登录

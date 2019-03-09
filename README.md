# CSDN_Blog_Format
---
将自己CSDN的文章转化为其编辑器里面的markdown格式
---
使用方法
1. 初始化对象
 - csdn = CSDN()
2. 设置输出路径
 - csdn.output = './'
3. 设置自己的CSDN账户名
 - csdn.user = ''
4. 设置自己的登录之后的cookie，可以自己点击一篇自己的文章编辑查看url的header得到，找到UserToken和UserInfo其中一个的值，这两个的值都是一样的
 - csdn.init_header('')
5. 运行
 - csdn.run()

---
如果不想要设置cookie，可以查看该项目的分支https://github.com/ddddyyyy/CSDN_Blog_Format/tree/login
可以通过使用账号密码登录

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
从12306的火车站列表文件里，利用正则表达式提取站点的中文名和英文缩写
"""

import re           #re模块包含所有正则表达式的功能
import requests     #Python访问HTTP资源的必备库
from pprint import pprint

url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9027"

#将 verify设置为False，Requests也能忽略对SSL证书的验证
response = requests.get(url, verify = False)

"""站点文件的格式
@bjb|北京北|VAP|beijingbei|bjb|0
@bjd|北京东|BOP|beijingdong|bjd|1
@bji|北京|BJP|beijing|bj|2
...
"""
#搜索字符串，以列表形式返回全部能匹配的子串。
stations = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]{3})', response.text)

#输出格式的对象字符串到指定的stream,最后以换行符结束。indent=4表示缩进4个空格
pprint(dict(stations),indent=4)

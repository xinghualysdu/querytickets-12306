#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""命令行查看火车票

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达

Example:
    tickets -t 北京 上海 2016-10-10
    tickets -dg 成都 南京 2016-10-10

"""

import requests
from stations import stations
from datetime import datetime
from docopt import docopt
from prettytable import PrettyTable
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class TrainsCollection:

    # split()就是将一个字符串分裂成多个字符串组成的列表。split()当不带参数时以空格进行分割，当带参数时，以该参数进行分割。
    header = "车次 站点 时间 历时 商务 一等 二等 高软 软卧 动卧 硬卧 软座 硬座 无座".split()

    """查询到的火车班次集合
    available_trains: 一个列表, 包含可获得的火车班次, 每个火车班次是一个字典
    options: 查询的选项, 如高铁, 动车, etc...
    """
    def __init__(self, raw_trains, options):
        self.raw_trains = raw_trains
        self.options = options

    def get_station_name(self,data_list):
        """获取站点中文名称信息
        导入的stations模块里存储的是一个dict，格式为 站点中文名称(key):站点英文缩写(value)
        而这里的形参data_list里包含的都是站点的英文缩写
        """
        first_station = data_list[4]
        last_station = data_list[5]
        from_station = data_list[6]
        to_station = data_list[7]

        #根据station这个dict的value(英文简称)找key(中文名称)
        for key in stations:
            if first_station == stations[key]:
                first_station_cn = key
            if last_station == stations[key]:
                last_station_cn = key
            if from_station == stations[key]:
                from_station_cn = key
            if to_station == stations[key]:
                to_station_cn = key

        #把几个表示站点名称的字符串用\n连接起来
        return '\n'.join([
            ('上车:' + from_station_cn),
            ('下车:' + to_station_cn),
            ('始发:' + first_station_cn),            
            ('终点:' + last_station_cn),
        ])

    def get_time(self, data_list):
        """获取上下车时间信息
        """
        return '\n'.join([
            ('上车:' + data_list[8]), 
            ('下车:' + data_list[9])
        ])


    def parse_train_data(self, data_list):
        """分析生成每列火车的信息(list)。
        此处的顺序必须与header相同
        """
        return [
            data_list[3],                       #车次
            self.get_station_name(data_list),   #站点
            self.get_time(data_list),           #上车/下车时间
            data_list[10],                      #历时
            data_list[32] or '--',              #商务座
            data_list[31] or '--',              #一等座
            data_list[30] or '--',              #二等座
            data_list[21] or '--',              #高级软卧
            data_list[23] or '--',              #软卧
            data_list[33] or '--',              #动卧
            data_list[28] or '--',              #硬卧
            data_list[24] or '--',              #软座
            data_list[29] or '--',              #硬座
            data_list[26] or '--']              #无座


    def need_print(self, data_list):
        """根据输入的列车类型(动车/高铁...)，判断查询到的火车列表(包含所有类型)是否要进行分析
        """
        station_train_code = data_list[3]
        initial = station_train_code[0].lower()
        return (not self.options or initial in self.options)


    def trains_form(self):
        """逐个判断所有火车信息: 生成data_list, 判断是否满足需要的火车票类型，对匹配的类型进行分析
        """
        for train in self.raw_trains:
            data_list = train.split('|')
            if self.need_print(data_list):
                yield self.parse_train_data(data_list)


    def pretty_print(self):
        """按格式显示
        先在表里添加header规定好每一列的顺序，再添加每列火车的信息，最后打印
        """
        table = PrettyTable()
        table._set_field_names(self.header)
        for train in self.trains_form():
            table.add_row(train)

        print(table)    




def cli():
    """command-line interface"""
    """docopt会根据我们在docstring中的定义的格式自动解析出参数并返回一个字典"""
    arguments = docopt(__doc__)

    #获取命令行输入的出发点、到达站、出发日期、选择的火车类型
    from_station = stations.get(arguments['<from>'])
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']
    options = ''.join([key for key, value in arguments.items() if value is True])

    #构建12306网站对应的URL
    url = "https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT".format(date, from_station,to_station)

    #发送URL，取消证书验证，并获得网站回复
    r = requests.get(url, verify = False)
    #获得网站回复结果
    trains = r.json()['data']['result'];

    #火车信息分析，并显示出来
    m = TrainsCollection(trains, options);
    m.pretty_print()


if __name__ == "__main__":
    cli()

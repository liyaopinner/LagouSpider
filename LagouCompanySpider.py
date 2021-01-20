# -*- coding: utf-8 -*-
import requests
import re
import json
import time
import math


class LagouCompanySpider:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            'Host': 'www.lagou.com'
        }
        self.home_url = 'https://www.lagou.com/gongsi/j62.html'
        self.postion_ajax = 'https://www.lagou.com/gongsi/searchPosition.json'
        self.position_list = ['产品','运营']
        self.company_list = ['字节跳动', '美团点评', '阅文集团', '蚂蚁金服', '爱奇艺', '360', '小红书', '喜马拉雅', '平安金服', '平安科技']
        self.company_dict = {'字节跳动': 62,
                             '美团点评': 50702,
                             '阅文集团': 28243,
                             '蚂蚁金服': 541761,
                             '爱奇艺': 1686,
                             '360': 436,
                             '小红书': 6542,
                             '喜马拉雅': 1373,
                             '平安金服': 161720,
                             '平安科技': 24748,
                             '平安银行': 141975,

                             }
        self.data = {
            'companyId': 62,
            'schoolJob': False,
            # 'positionFirstType': '全部',
            'positionFirstType': '产品',
            # 'city': '上海',
            'pageNo': 1,
            # 最大就是10
            'pageSize': 10
        }
        self.time_sleep = 60

    @staticmethod
    def get_cookies():
        url = 'https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput='
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
        cookies = requests.get(url=url, headers=headers, allow_redirects=False).cookies
        return cookies

    def get_header(self):
        home_resp = requests.get(self.home_url, headers=self.headers)
        # cookies = home_resp.cookies.get_dict()
        self.headers['X_Anti_Forge_Token'] = re.search(r"window.X_Anti_Forge_Token = '(.*?)'", home_resp.text).group(1)
        self.headers['X_Anti_Forge_Code'] = re.search(r"window.X_Anti_Forge_Code = '(.*?)'", home_resp.text).group(1)
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.headers['Referer'] = self.home_url

    def save_parse_data(self, parse_data_str, save_type):
        if save_type == 'company':
            with open(f'{self.company_name + "_" + self.data["positionFirstType"]}拉钩.csv', mode='a',
                      encoding='utf-8', newline='') as f1:
                f1.writelines(parse_data_str + '\n')
            with open(f'{self.company_name + "_" + self.data["positionFirstType"]}_拉钩_gbk.csv', mode='a',
                      encoding='utf-8', newline='') as f2:
                f2.writelines(parse_data_str + '\n')
        if save_type == 'all':
            with open('拉钩汇总.csv', mode='a',
                      encoding='utf-8', newline='') as f2:
                f2.writelines(parse_data_str + '\n')
            # with open('拉钩汇总_gbk.csv', mode='a',
            #           encoding='gbk', newline='') as f2:
            #     f2.writelines(parse_data_str + '\n')

    def data_parse(self, data, position_type):
        position_return = json.loads(data.text)
        position_result = position_return['content']['data']['page']['result']
        for i in position_result:
            parse_data_temp = []
            parse_data_temp.append(position_type)
            # parse_data_temp.append(i['financeStage'].replace(' ',''))
            parse_data_temp.append(i['companyName'].replace(' ',''))
            # parse_data_temp.append(i['companySize'].replace(' ',''))
            # parse_data_temp.append(i['industryField'].replace(' ',''))
            position_url = 'https://www.lagou.com/jobs/{position_id}.html'.format(position_id=i['positionId'])
            parse_data_temp.append(position_url)
            parse_data_temp.append(i['positionName'].replace(' ',''))
            parse_data_temp.append(i['city'].replace(' ',''))
            parse_data_temp.append(i['salary'].replace(' ',''))
            parse_data_temp.append(i['workYear'].replace(' ',''))
            parse_data_temp.append(i['education'].replace(' ',''))
            # parse_data_temp.append(i['positionAdvantage'].replace(' ',''))
            parse_data_temp_str = re.sub("\[|\]|\'", "", str(parse_data_temp))
            parse_data_temp_str = re.sub(" ", "", str(parse_data_temp_str))

            self.save_parse_data(parse_data_temp_str, 'company')
            self.save_parse_data(str(parse_data_temp_str), 'all')

            # parse_data_str = re.sub("\[|\]|\'", "", str(parse_data_temp))

    def main(self):
        self.get_header()
        for company in self.company_list:
            self.data['companyId'] = self.company_dict[company]
            self.company_name = company
            self.home_url = 'https://www.lagou.com/gongsi/j{id}.html'.format(id=self.company_dict[company])
            self.headers['Referer'] = self.home_url
            cookies = self.get_cookies()
            for position in self.position_list:
                self.data['positionFirstType'] = position
                position_resp_init = requests.post(self.postion_ajax, data=self.data, headers=self.headers,
                                                   cookies=cookies)
                position_return = json.loads(position_resp_init.text)
                total_cnt = int(position_return['content']['data']['page']['totalCount'])
                total_page_cnt = math.ceil(total_cnt / self.data['pageSize'])
                print("***开始爬取 %s %s岗位，共计 %d 条***" % (company, position, total_cnt))
                for page in range(1, total_page_cnt):
                    if page % 5 == 0:
                        print("***当前第 %d 页，共计 %d 页***" % (page, total_page_cnt))
                        cookies.update(self.get_cookies())
                    self.data['pageNo'] = page
                    position_resp = requests.post(self.postion_ajax, data=self.data, headers=self.headers,
                                                  cookies=cookies)
                    self.data_parse(position_resp, position)
                print("*** %s %s 岗位爬取完毕" % (company, position))


# import codecs
# with open('拉钩汇总_gbk.csv', mode='r',encoding='utf-8', newline='') as f:
#     utfstr = f.read()
#     f.close()
# # 把UTF8字符串转码成ANSI字符串
# outansestr = utfstr.encode('gbk',errors = 'ignore')
# # 使用二进制格式保存转码后的文本
# f = open('拉钩汇总_gbk.csv', 'wb')
# f.write(outansestr)
# f.close()

if __name__ == '__main__':
    LagouCompanySpider().main()

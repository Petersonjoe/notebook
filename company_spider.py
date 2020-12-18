import re
import json
import random
import urllib3
import requests
import pandas as pd
from time import sleep
from functools import reduce
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# to declare a random header for the 403 error that prevents spider
headers = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
    "Opera/9.25 (Windows NT 5.1; U; en)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12",
    "Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9",
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
]

selected_header = {'User-Agent': random.choice(headers)}
# print(f'User-Agent re-direct to: {selected_header["User-Agent"]}')

# API on 爱企查
PID_URL_PRE = 'https://aiqicha.baidu.com/s?q={company_name}'
BASIC_PAGE_PRE = 'https://aiqicha.baidu.com/detail/basicAllDataAjax?pid={pid}'
RISK_LIST = 'https://aiqicha.baidu.com/risk/unionRiskAjax?pid={pid}'
JUDGE_DOC_MAX = 20

def searchURL(url: str='') -> str:
    """    
    This function will return the response string from https://aiqicha.baidu.com/ with url parameters.

    Parameters
    ---
    url: The input url query string.

    Return
    ---
    String, the URL returned text raw data.
    """

    req_body = requests.get(url, headers=selected_header, verify=False)
    _response = req_body.text.encode('utf-8').decode('unicode-escape')
    _response = re.sub("(\n^$\n)","",_response, flags=re.M)  # remove emtpy line
    _response_str = re.sub("($\s+^)","",_response, flags=re.M)  # remove case2

    if (_response_str is None) or (len(_response_str)==0):
        print(f"Error: NO response from the url query! <The url: {url} is invalid, no data returned.>")
        return None

    return _response_str

class CompanySpider(object):
    """
    The company spider will search company data on https://aiqicha.baidu.com/.
    Function modules needs to be added later

    """
    __pid__ = None
    __domain__ = 'https://aiqicha.baidu.com'

    def __init__(self, company_name: str='') -> None:
        """
        Instantiate the spider, with given company name.
        NO return value, the company PID can be fetched.

        Sample
        ---
        test_company = '浙江中外运有限公司宁波泛洲分公司'
        spider1 = CompanySpider(test_company)
        company_pid = spider1.PID  # PID is the unique identifier for a company in 爱企查
        """
        if company_name == '':
            print('Error: wrong call function, please specify the company name.')
        self._company_name = company_name

        pattern = '(.*)"resultList":\s*\[\{"pid":\s*"([0-9]+)",?(.*)\}\};'
        response_str = searchURL(PID_URL_PRE.format(company_name=self._company_name))
        parse_res1 = re.search(pattern, response_str, re.M|re.I|re.S)
        # print(response_str)
        if parse_res1 is None:
            self.__pid__ = None
            return None
        else:
            self.__pid__ = parse_res1.group(2)
            return None

    @property
    def PID(self) -> str:
        """
        Once the class instantiated, then one can get the PID, which is the ID for a company in https://aiqicha.baidu.com/.
        """
        return self.__pid__
    
    def __unionRisks__(self) -> tuple:
        """
        This function is to extract the union risk list for a company. 
        It can be rewritten to expand the return tuple:
        
        the mapping for risk type:
        C00012  经营异常
        C00043  清算组信息
        C00017  裁判文书  <-- get done
        C00019  行政处罚
        C00034  动产抵押
        C00040  简易注销公告
        C00086  开庭公告  <-- get done
        C00088  立案信息
        
        Take the PID as the entrance, get the lawsuit details with below links:
        https://aiqicha.baidu.com/risk/unionRiskAjax?pid={pid}
        
        RETURN a tuple (裁判文书列表, 开庭公告列表, 总数)
        """
        response_str = searchURL(RISK_LIST.format(pid=self.__pid__))
        response_dict = json.loads(response_str)
        
        if ( 'total' not in response_dict['data'].keys() ) or \
            ( 'list' not in response_dict['data'].keys() ):
            print(f'Warning: No judgement docs found for {self._company_name}.')
            return (None, None, None)

        _total_risks = response_dict['data']['total']
        _union_risks = response_dict['data']['list']

        if (int(_total_risks) == 0) or (_union_risks is None):
            print(f"Warning: No judgement docs found for {self._company_name}.")
            return (None, None, None)
        
        _judgement_docs = {}
        _open_notice = {}
        if _total_risks > 0:
            for risk in _union_risks:
                if risk['code'] == 'C00017':
                    _judgement_docs = risk['list']
                elif risk['code'] == 'C00086':
                    _open_notice = risk['list']
                else:
                    pass
            return (_judgement_docs, _open_notice, _total_risks)
        else:
            return (None, None, None)

    def getCompanyBasic(self) -> pd.DataFrame:
        """
        This function will get company basic data in https://aiqicha.baidu.com/. Input should be the PID for a company. 

        The API for company basic data is: https://aiqicha.baidu.com/detail/basicAllDataAjax?pid={pid}
        pid can be obtained by calling the PID function, details please refer to CompanySpider.PID     
        """
        response_str = searchURL(BASIC_PAGE_PRE.format(pid=self.__pid__))
        response_dict = json.loads(response_str)
        basic_data = response_dict['data']['basicData']

        # store the data into a dict
        _stored_data = {}
        _stored_data['公司代码'] = self.__pid__
        _stored_data['公司名称'] = basic_data["entName"]
        _stored_data['公司状态'] = basic_data["openStatus"]
        _stored_data['公司类型'] = basic_data["entType"]
        _stored_data['注册代码'] = basic_data["regNo"]
        _stored_data['税务代码'] = basic_data["taxNo"]
        _stored_data['营业范围'] = basic_data["scope"]
        _stored_data['注册地址'] = basic_data["regAddr"]
        _stored_data['法人代表'] = basic_data["legalPerson"]
        _stored_data['注册日期'] = basic_data["startDate"]
        _stored_data['存续时间'] = basic_data["openTime"]
        _stored_data['注册资本'] = basic_data["regCapital"]
        _stored_data['行业'] = basic_data["industry"]
        _stored_data['电话'] = basic_data["telephone"]
        _stored_data['所在区域'] = basic_data["district"]
        _stored_data['监管当局'] = basic_data["authority"]
        _stored_data['公司描述'] = basic_data["describe"]
        _, _, _stored_data['关联风险总数'] = self.__unionRisks__()

        return pd.DataFrame(
            _stored_data, 
            index=[0],
            columns=['公司代码','公司名称','公司状态','公司类型','注册代码','税务代码','营业范围','注册地址','法人代表','注册日期','存续时间','注册资本','行业','电话','所在区域','监管当局','公司描述','关联风险总数']
        )
    
    def getJudgementDocs(self) -> pd.DataFrame:
        """
        This function is to extract the Judgement Docs (裁判文书) List for a company.
        
        Take the PID as the entrance, get the lawsuit details with below links:
        https://aiqicha.baidu.com/detail/lawWenshuAjax?pid=53292518732253&f={"causeType3":"1037:002007001010"}&size=13

        DataFrame schema
        ---
        columns=['原公司ID','案件身份公司ID','案件身份公司名称','案件身份','案由','案件名称','案号','裁决日期','文书代码', '文书URL']
        """

        url_prefix = 'https://aiqicha.baidu.com/detail/lawWenshuAjax?pid=53292518732253&f={"causeType3":"'
        url_suffix = '"}&size='
        judgement_doc_list, _, _ = self.__unionRisks__()

        if judgement_doc_list is None:
            return None

        # create an empty DataFrame
        _stored_data = pd.DataFrame(
            columns=[
                    '原公司ID',
                    '案件身份公司ID',
                    '案件身份公司名称',
                    '案件身份',
                    '案由',
                    '案件名称',
                    '案号',
                    '裁决日期',
                    '文书代码',
                    '文书URL',
                    '裁决文书总数'
                    ]
            )

        total_judge_num = len(judgement_doc_list)
        _count = 0
        for doc in judgement_doc_list:
            _count += 1
            _key, _num = doc['key'], doc['num']

            # controlling for anti-spider
            if _count > JUDGE_DOC_MAX:
                print('Warning: NUM of judgement doc details exceeds the tolerance 20.')
                break

            if int(_num) < 1:
                continue
            else:
                _url = url_prefix + _key + url_suffix + _num

                sleep(30)  # to bypass the anti-spider for 2 consecutive requests
                response_str = searchURL(_url)
                response_dict = json.loads(response_str)
                response_list = response_dict['data']['list']

                if not response_dict:
                    continue

                for _info in response_list:
                    _tmp_stored_data = {}
                    _tmp_stored_data['原公司ID'] = self.__pid__
                    _tmp_stored_data['案件身份公司ID'] = _info['bid']
                    _tmp_stored_data['案件身份公司名称'] = _info['compName']
                    _tmp_stored_data['案件身份'] = _info['role']
                    _tmp_stored_data['案由'] = _info['type']
                    _tmp_stored_data['案件名称'] = _info['wenshuName']
                    _tmp_stored_data['案号'] = _info['caseNo']
                    _tmp_stored_data['裁决日期'] = _info['verdictDate']
                    _tmp_stored_data['文书代码'] = _info['wenshuId']
                    _tmp_stored_data['文书URL'] = self.__domain__ + _info['detailUrl']
                    _tmp_stored_data['裁决文书总数'] = total_judge_num

                    _stored_data = _stored_data.append(_tmp_stored_data, ignore_index=True, verify_integrity=False, sort=None)

        if not _stored_data.empty:
            return(_stored_data)
        else:
            return None

    def getOpenNoticeDetails(self) -> pd.DataFrame:
        """
        This function is to extract the Open Notice (开庭公告) List for a company.
        
        Take the PID as the entrance, get the Open Notice details with below links:
        https://aiqicha.baidu.com/c/opennoticeajax?pid=53292518732253

        DataFrame schema
        ---
        columns=['原公司ID','被告公司ID','被告公司名称','开庭日期','案号','案由','管辖区域','承办部门','审判长','法院','被告','开庭公告详情','原告','关联被告','开庭公告总数']
        """
        
        url = 'https://aiqicha.baidu.com/c/opennoticeajax?pid={pid}'
        _, open_notice_list, _ = self.__unionRisks__()

        if open_notice_list is None:
            return None

        # create schema
        _stored_data = pd.DataFrame(
            columns=[
                    'DataId',
                    '原公司ID',
                    '被告公司ID',
                    '被告公司名称',
                    '开庭日期',
                    '案号',
                    '案由',
                    '管辖区域',
                    '承办部门',
                    '审判长',
                    '法院',
                    '被告',
                    '开庭公告详情',
                    '原告',
                    '关联被告',
                    '开庭公告总数'
                    ]
            )

        total_notice_num = len(open_notice_list)
        print(f'Info: Total open notice number is {total_notice_num}.')
        _count = 0
        for notice in open_notice_list:
            _pid, _num = notice['pid'], notice['num']

            # controlling for anti-spider
            _count += 1
            if _count > JUDGE_DOC_MAX:
                print("Warning: NUM of open notice details exceeds the tolerance 20.")
                break

            if int(_num) < 1:
                continue
            else:
                _url = url.format(pid=_pid)
                
                sleep(30)  # to bypass the anti-spider for 2 consecutive requests
                response_str = searchURL(_url)
                response_dict = json.loads(response_str)
                response_list = response_dict['data']['list']

                for _info in response_list:
                    _tmp_stored_data = {}
                    _tmp_stored_data['DataId'] = _info['dataId']
                    _tmp_stored_data['原公司ID'] = self.__pid__
                    _tmp_stored_data['被告公司ID'] = _pid
                    _tmp_stored_data['被告公司名称'] = _info['ename']
                    _tmp_stored_data['开庭日期'] = _info['hearingDate']
                    _tmp_stored_data['案号'] = _info['caseNo']
                    _tmp_stored_data['案由'] = _info['caseReason']
                    _tmp_stored_data['管辖区域'] = _info['region']
                    _tmp_stored_data['承办部门'] = _info['department']
                    _tmp_stored_data['审判长'] = _info['judge']
                    _tmp_stored_data['法院'] = _info['court']
                    _tmp_stored_data['被告'] = _info['ename']
                    _tmp_stored_data['开庭公告详情'] = _info['detailUrl']
                    _tmp_stored_data['开庭公告总数'] = total_notice_num

                    _tmp_plaintiff = reduce(lambda x,y: x+','+y, _info['plaintifflist'])
                    _tmp_defendant = reduce(lambda x,y: x+','+y, _info['defendantlist'])

                    _tmp_stored_data['原告'] = _tmp_plaintiff
                    _tmp_stored_data['关联被告'] = _tmp_defendant

                    _stored_data = _stored_data.append(_tmp_stored_data, ignore_index=True, verify_integrity=False, sort=None)

        if not _stored_data.empty:
            return _stored_data
        else:
            return None

    def placeholderFunc(self) -> None:
        """
        To extend any further feature and function for the spider.
        """
        pass


if __name__ == '__main__':
    # test code here

    # 1. find the company PID
    test_company = '上海泛亚航运有限公司'
    spider1 = CompanySpider(test_company)
    # a, b, c = spider1.__unionRisks__()
    print(spider1.getJudgementDocs())

    # 2. analyze the URL response string
    # 浙江中外运宁波泛洲 - 55240810372165
    # https://aiqicha.baidu.com/risk/riskindex?pid=55240810372165&tab=2  --risk index page
    # https://aiqicha.baidu.com/risk/unionRiskAjax?pid=55240810372165  --risk list

    # 通过risk list将55240810372165和53292518732253关联起来
    # -- 按照risk list中 文书代码 的第一个元素，用key，num组装如下<cause type尚未确定>：
    # https://aiqicha.baidu.com/detail/lawWenshuAjax?pid=53292518732253&f={"causeType3":"1037:002007001010"}&size=13
    # url = 'https://aiqicha.baidu.com/detail/lawWenshuAjax?pid=53292518732253&f={"causeType3":"'+ '1037:002007001010' +'"}&size=13'
    # print(url)
    # req_body = requests.get('https://aiqicha.baidu.com/c/opennoticeajax?pid=53292518732253', headers=selected_header, verify=False)
    # response_body = req_body.text.encode('utf-8').decode('unicode-escape')
    # response_body = re.sub("(\n^$\n)","",response_body, flags=re.M)
    # response_body = re.sub("($\s+^)","",response_body, flags=re.M)
    # print(response_body)
    # response_dict = json.loads(response_body)
    # basic_data = response_dict['data']['basicData']
    # print(basic_data)

    # pattern = '(.*)"resultList":\s*\[\{"pid":\s*"([0-9]+)",?(.*)\}\};'
    # parse_res1 = re.search(pattern, response_str, re.M|re.I|re.S)
    # pid = parse_res1.group(2)



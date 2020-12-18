import os
import sys
import logging
import pandas as pd
from time import sleep
from company_spider import CompanySpider
from random import randint
import argparse

# Macro Definition - Input
# SOURCE_FILE = './2020年1月至8月车辆地磅系统.xls'
# SHEET_NAME = '2020年1月至8月车辆地磅明细'
# COL_NAME = '供应商或承运商'
COLS = ['公司代码','公司名称','公司状态','公司类型','注册代码','税务代码','营业范围','注册地址','法人代表','注册日期','存续时间','注册资本','行业','电话','所在区域','监管当局','公司描述','关联风险总数']

# Macro Definition - Output
TMP_FILE = 'company_basic_info.csv.tmp'
RESULT_FILE = 'company_basic_info.csv'

# argument settings
parser = argparse.ArgumentParser(description='Usage of aiqicha company spider.')
parser.add_argument('--source-file', '-sf', help='mandatory, source data file, containing ship vendor company name.', required=True)
parser.add_argument('--sheet-name', '-sn', help='optional, if source data file is excel file, then must provide this.')
parser.add_argument('--col-name', '-cn', help='optional, column name, if source data file is excel file, then must provide this')
args = parser.parse_args()

# log settings
log_fmt = "%(asctime)s  %(levelname)s::%(message)s"
date_fmt = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG, format=log_fmt, datefmt=date_fmt)

# logging.debug("This is a debug log.")
# logging.info("This is a info log.")
# logging.warning("This is a warning log.")
# logging.error("This is a error log.")
# logging.critical("This is a critical log.")

if __name__ == '__main__':
	company_list = []
	exist_pid = []
	
	# argparse的调用方法
	logging.info('-'*30)
	logging.info(f'source file name: {args.source_file}, sheet name: {args.sheet_name}, column name: {args.col_name}')
	logging.info('-'*30)

	# read input, search file number
	if (args.source_file is not None) and \
	   ( (args.source_file[-4:len(args.source_file)]=='.xls') or (args.source_file[-5:len(args.source_file)]=='.xlsx') ) and \
	   ( (args.sheet_name is None) or (args.col_name is None) ):
		logging.error("No sheet_name and col_name provided.")
		sys.exit(1)

	# current data
	try:
		current = pd.read_csv(RESULT_FILE, header=[0], index_col=None)
		current = current[COLS]
		exist_pid = current["公司代码"].drop_duplicates().values.tolist()
		logging.info(exist_pid)
	except pd.errors.EmptyDataError as ec:
		current = pd.DataFrame(columns=COLS)
		pass
	
	logging.info('-'*30)
	logging.info('-'*30+'Existing Data'+'-'*30)
	logging.info(current)
	logging.info('-'*30)

	# simple data ETL
	if (args.source_file[-4:len(args.source_file)]=='.xls') or (args.source_file[-5:len(args.source_file)]=='.xlsx'):
		df = pd.read_excel(
		    args.source_file,
		    sheet_name=arg.sheet_name,
		    header=[0],
		    index_col=None
		    )
		# remove cols that are all null or no title
		for col in df.columns:
			if df[col].count() == 0:
				logging.info(col + ' is all null.')
				df.drop(labels=col, axis=1, inplace=True)

			if (len(col) > 8) and (col[0:9] == 'Unnamed:'):
				logging.info(col + ': Unnamed column catched.')
				df.drop(labels=col, axis=1, inplace=True)

		company_list = df[args.col_name].drop_duplicates().values.tolist()

	elif (args.source_file[-4:len(args.source_file)]in ['.csv', '.txt']):
		df = pd.read_csv(
			args.source_file,
			header=None,
			names=['ship_vendor'],
			index_col=None
			)
		company_list = df['ship_vendor'].drop_duplicates().values.tolist()

	logging.info('The number of company counted: {}'.format(len(company_list)))
	logging.info('-'*30)

	company_basic = pd.DataFrame(columns=COLS)

	count = 0
	for company_name in company_list:
		count += 1
		logging.info('Process the {0}th company: {1}'.format(count, company_name))

		company = CompanySpider(company_name)
		# logging.info(f'Type of PID -- {type(company.PID)}')
		# logging.info(f'Type of PID -- {type(exist_pid[0])}')

		if not company.PID:
			logging.warning(f'No info returned for COMPANY: {company_name} in aiqicha.baidu.com.')
		else:
			if company.PID in exist_pid:
				logging.info(f'{company.PID} exists, will skip {company_name}.')
				continue
			else:
				sleep(15)
				basic_info = None
				basic_info = company.getCompanyBasic()
				if basic_info is not None:
					company_basic = company_basic.append(basic_info)
		
		logging.info('-'*30)


	logging.info('-'*30)
	logging.info('-'*30+'Incremental Data'+'-'*30)
	logging.info(company_basic)
	logging.info('-'*30)	

	merge_flag = 0
	_current = pd.DataFrame(columns=COLS)
	with open(TMP_FILE, 'w', encoding='utf-8') as tmp_file:
		try:
			# _current = current.append(company_basic)
			# from pdb import set_trace
			# set_trace()
			
			if current.empty:
				_current = company_basic

			if company_basic.empty:
				_current = current

			if (not current.empty) and (not company_basic.empty):
				_current = pd.concat([current, company_basic])

			logging.info('-'*30)
			logging.info('-'*30+'Final Merged Data'+'-'*30)
			logging.info(company_basic)
			logging.info('-'*30)

			_current = _current.dropna(axis=0)
			_current.to_csv(tmp_file)
		except Exception as ec:
			merge_flag = 1
			logging.error("Merge incremental data failed!")
			logging.info(ec)
		finally:
			pass

	if merge_flag == 1:
		import os
		os.remove("company_basic_info.csv.tmp")
	else:
		import os
		os.remove(RESULT_FILE)
		os.rename('company_basic_info.csv.tmp', RESULT_FILE)
		logging.info("Merge incremental data success!")


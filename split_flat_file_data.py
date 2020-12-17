import os
import argparse
import logging

# argument settings
parser = argparse.ArgumentParser(description='Usage of aiqicha company spider.')
parser.add_argument('--source', '-s', help='mandatory, source data file to be split.', required=True)
parser.add_argument('--number', '-n', help='mandatory, the number of text pieces.')
args = parser.parse_args()

# # log settings
# log_fmt = "%(asctime)s  %(levelname)s::%(message)s"
# date_fmt = "%m/%d/%Y %H:%M:%S %p"
# logging.basicConfig(level=logging.debug, format=log_fmt, datefmt=date_fmt)

if __name__ == '__main__':
	
	step = int(args.number)

	data = open(args.source, 'r', encoding='utf-8').readlines()
	print(f'Length of file: {len(data)}, type of data: {type(data)}, type of args.number: {type(args.number)}')
	print(data)

	file_num = int(len(data)/step)

	for i in range(file_num):
		_data = data[step*i:step*(i+1)]

		with open(f'split_file_{i}.txt', 'w', encoding='utf-8') as sf:
			sf.writelines(_data)

	if len(data) == file_num*step:
		pass
	else:
		_data = data[file_num*step+1: len(data)]
		with open(f'split_file_{file_num}.txt','w', encoding='utf-8') as sf:
			sf.writelines(_data)


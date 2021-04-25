# !/usr/bin/env python
# --------------------------------------------------------------
# File:          test_function.py
# Project:       lymo
# Created:       Thursday, 22nd April 2021 1:46:35 am
# @Author:       Molin Liu, MSc in Data Science, University of Glasgow
# Contact:       molin@live.cn
# Last Modified: Thursday, 22nd April 2021 1:46:53 am
# Copyright  © Rockface 2019 - 2021
# --------------------------------------------------------------
import pytest
import chardet, os
import sys 
sys.path.append('../') 
import TransEncoding

cn_encode=['utf-8', 'gbk', 'gb2312', 'gb18030']

def create_simple_test_example():
	file_name = "simple_test_example.txt"
	with open(file_name, 'wb') as f:
		text = "当使用import语句导入模块时，\n解释器会搜索当前模块所在目录以及sys.path指定的路径去找需要import的模块，\n所以这里是直接把上级目录加到了sys.path里。"
		data = text.encode('GBK')
		f.write(data)
	return file_name

def create_mix_test_example():
	file_name = "mix_test_example_a.txt"
	text = []
	with open('test_text.txt', 'r') as f:
		text = f.readlines()
	with open(file_name, 'wb') as f:
		output_data = []
		for index, line in enumerate(text):
			output_data.append(line.encode(cn_encode[index%4]))
		f.write(b'\n'.join(output_data))
	return file_name

def test_simple_transfer():
	file_name = create_simple_test_example()
	out_file = 'simple_test_example_out.txt'
	TransEncoding.simple_transfer('GBK', file_name, out_file)
	with open(out_file, 'rb') as f:
		data = f.read()
		result = chardet.detect(data)
		assert (result['encoding']=='utf-8')&(result['confidence']>0.98)

def test_mix_transfer_a():
	file_name = create_mix_test_example()
	TransEncoding.mix_transfer(file_name, 'others')
def test_clean():
	files = [
		'simple_test_example.txt',
		'mix_test_example_a.txt',
		'mix_test_example_b.txt',
		'mix_test_example_c.txt'
		]
	for file in files:
		if os.path.exists(file):
			os.remove(file)
# !/usr/bin/env python
# --------------------------------------------------------------
# File:          TransEncoding.py
# Project:       lymo
# Created:       Thursday, 22nd April 2021 12:29:34 am
# @Author:       Molin Liu, MSc in Data Science, University of Glasgow
# Contact:       molin@live.cn
# Last Modified: Thursday, 22nd April 2021 12:29:38 am
# Copyright  © Rockface 2019 - 2021
# --------------------------------------------------------------

import os, chardet, tqdm
from multiprocessing import cpu_count, Pool
import logging
import datetime
today = datetime.date.today()
time = today.strftime("%Y-%m-%d")
logging.basicConfig(
	level=logging.INFO, 
	filename="Log/"+time+".log",
	filemode='a',
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def getFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

def simple_transfer(type, file_path, out_path=None):
	"""
	simple_transfer [summary]

	Args:
		type (str): File's encoding type
		file_path (str): Path to the file
		out_path (str, optional): Path to the output file. Defaults to None.

	Returns:
		[bool]: whether transfer the encoding type successfully.
	"""	
	with open(file_path, 'rb') as f:
		data = f.read()
		try:
			data = data.decode(type).encode('utf-8')
		except:
			return False

		with open(out_path if out_path else file_path, 'wb') as out_f:
			out_f.write(data)

		return True

def mix_transfer(file_path, mode='others'):
	"""
	mix_transfer 

	Each line of the files will be read and try to decode with several options
	then encode into utf-8

	@Note: 
		Input and output will use binary to transfer the file.
	@Todo:
		1. Finish mix_transfer processing.
		2. Test all function
	Args:
		file_path ([type]): [description]
	"""	
	
	if mode=='inplace':
		outfile = file_path
	elif mode=='others':
		if not os.path.exists('out'):
			os.mkdir('out')
		outfile = os.path.join('out', os.path.basename(file_path))
	else:
		raise NotImplementedError
	with open(file_path, 'rb') as f:

		lines = f.readlines()
		output_data = []

		for line in lines:
			temp_line = line
			temp_result = chardet.detect(line)
			# If the line is pure code.
			if temp_result['confidence']>0.98:
				# Check if the line has already had encoding type.
				if temp_result['encoding']!='ascii':
					try:
						temp_line = line.decode(temp_result['encoding']).encode('utf-8')
					except:
						temp_line = repair_encoding(line)
				else:
					# In word repair
					pass
			output_data.append(temp_line)
		
		with open(outfile, 'wb') as f_out:
			f_out.write(b''.join(output_data))
def repair_encoding(raw_line):
	# Encoding type try:

	try:
		temp = raw_line.decode('utf-8')
		temp = temp.encode('gbk')
		temp = temp.decode('utf-8')
		return temp
	except:
		return raw_line
	
def _transfer(file_path):
	with open(file_path, 'rb') as f:
		data = f.read()
		result = chardet.detect(data)
		if result['encoding']!=None and result['encoding']!='utf-8':
			if result['confidence']>0.9:
				if not simple_transfer(result['encoding'], file_path):
					logger.error("{encoding} -> UTF-8 FAILS: {file_path}".format(encoding=result['encoding'], file_path = file_path))
					mix_transfer(file_path)
			else:
				mix_transfer(file_path)

class TransEncoding:
	def __init__(self) -> None:
		pass
		
	def transfer(self, project_dir):
		all_files = getFiles(project_dir)
		try:
			workers = cpu_count()
		except NotImplementedError:
			workers = 1
		pool = Pool(processes=workers)
		
		for _ in tqdm.tqdm(pool.imap_unordered(_transfer, all_files), total=len(all_files)):
			pass
		pool.close()
		pool.join()
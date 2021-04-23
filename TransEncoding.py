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

def mix_transfer(file_path):
	with open(file_path, 'rb') as f:
		lines = f.readlines()
		for line in lines:
			temp_result = chardet.detect(line)

			if temp_result['encoding']!='ascii':
				if temp_result['confidence']>0.95:
					try:
						temp_line = line.decode(temp_result['encoding'])
					except:
						pass

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
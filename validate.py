#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Python script to verify the validity of the swagger docs"""
import argparse
import collections
import json
import sys
import os

parser= argparse.ArgumentParser()
parser.add_argument("directory", help="Full directory path of swagger docs",type=str)
input_dir= parser.parse_args().directory

## List of all Error messages
errorMessages= {"scheme_empty":"Schemes must be defined","scheme":"Schemes should be https","host":"Hostname should be www.dbs.com/sandbox", "overview":"swagger description should have the words 'Overview', 'Version History', 'Authentication', '<security-definitions>', 'Pagination', 'FAQ', 'Known Issues' and 'Throttling'","securityDefinitions":"Security definitions not found.","summary":"Summary needs to be capitalized.","get":"Replace 'get' with 'Retrieve'.","accept":"Change description to 'Specifies the acceptable version of the message set. If not specified, the latest version of the API will be considered. Example: 1.2'","no-accept":"No accept-version found.","uuid":"No uuid found.","default":"Default error responses needs to be removed","no-e500":"Error 500 not present","e500":"Error 500 needs a schema defined.","201":"Error 201 is only for POST methods"}
overview_headers=["Overview","Version History","Authentication","<security-definitions>","Pagination","Frequently Asked Question","Known Issues","Throttling"]
def check_overview(headers,description):
	missing=[i for i in headers if i not in description]
	return missing
def check_caps(s):
    return s[0].isupper()

def errorLog(title,error,method=None):
	if method== None:
		error_msg="{} : "+(errorMessages[error])
		print(error_msg.format(title))
	else:
		error_msg="Method {}/{}: "+(errorMessages[error])
		print(error_msg.format(title,method))
	
def validate(input):
	title= input.get("info").get("title")
	print("Checking {}".format(title))
	print("==============================================")
	## Check schemes and host names
	if input.get("schemes") == None:
		errorLog(title,"scheme_empty")
	if input.get("schemes") != None and "https" not in input.get("schemes"):
		errorLog(title,"scheme")
	if "www.dbs.com/sandbox" not in input.get("host"):
		errorLog(title,"host")
	## Check for Overview sections
	description= input.get("info").get("description")
	headers_missing=check_overview(overview_headers,description)
	if len(headers_missing) != 0:
		print("Sections missing: "+", ".join(headers_missing))
		errorLog(title,"overview")
	## Check for security definitions
	if "securityDefinitions" not in input:
		errorLog(title,"securityDefinitions")
	## Get list of api methods
	apis = input.get("paths")
	for k in apis:
		api_set = apis.get(k).items()
		## Get/Post on the api path
		for tuple in api_set:
			api_method, api= tuple[0], tuple[1]
			summary = api.get("summary")
			## Check capitalized summary
			if check_caps(summary) is False:
				errorLog(k,"summary",api_method)
			if summary.startswith("get"):
				errorLog(k,"get",api_method)
			param_list = [d['name'] for d in api.get("parameters")]
			parameters = api.get("parameters")
			## Check accept-version header and description
			if "accept-version" in param_list:
				for item in parameters:
					if item.get("name") == "accept-version":
						if item.get("description") != "Specifies the acceptable version of the message set. If not specified, the latest version of the API will be considered. Example: 1.2":
							errorLog(k,"accept",api_method)
			else:
				errorLog(k,"no-accept",api_method)
			## Check uuid 
			if "uuid" not in parameters:
				errorLog(k,"uuid",api_method)
			## Check error responses
			responses =  api.get("responses")
			if api_method=="get" and "201" in responses:
				errorLog(k,"201",api_method)
			if "default" in responses:
				errorLog(k,"default",api_method)
			if responses.get("500")== None:
				errorLog(k,"no-e500",api_method)
			else:
				if responses.get("500").get("schema")== None:
					errorLog(k,"e500",api_method)
	if input.get("definitions").get("errorList")==None:
		print("{}: Error List definition missing".format(title))
	print("\nInspection of {} done".format(title))
			

def fileopen(data):
	with open(data, mode= "r") as file_data:
		content = json.load(file_data, strict=False, object_pairs_hook=collections.OrderedDict)
	return content

# def filewrite(data, input):
	# with open(data, mode="w") as file_data:
		# json.dump(input,file_data,indent=4)

def check_directory(dir):
	dir_contents=[]
	for filename in os.listdir(dir):
		try:
			if filename.endswith(".json"):
				filename= os.path.join(input_dir,filename)
				file_contents=fileopen(filename)
				dir_contents.append(file_contents)
		except Exception as e:
			print("{} is not a valid JSON file".format(filename))
			print('Error on line {}\n\n'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
			continue
	return dir_contents
		
def main():
	file_list= check_directory(input_dir)
	for item in file_list:
		validate(item)
		print("\n\n")
	
	

if __name__ == '__main__':
	main()
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Python script to MODIFY swagger docs to its correct format"""
import argparse
import collections
import json
import os
import sys


parser= argparse.ArgumentParser()
parser.add_argument("directory", help="Full directory path of swagger docs",type=str)
input_dir= parser.parse_args().directory

overview_headers=["Overview","Version History","Authentication","<security-definitions>","Pagination","Frequently Asked Question","Known Issues","Throttling"]
def check_overview(headers,description):
	missing=[i for i in headers if i not in description]
	return missing

def replace_at_index(tup, ix, val): 
	return tup[:ix] + (val,) + tup[ix+1:]

def check_caps(s):
    return s[0].isupper()
	
def modify(input):
	title= input.get("info").get("title")
	print("Checking {}".format(title))
	print("==============================================")
	## Check for Overview sections
	description= input.get("info").get("description")
	if "# Overview" not in description:
		print("{}: Overview sections added, please check".format(title))
		new_description="# Overview\n {} \n\n# Version History\nVersion | Release date | Link to documentation\n--------|--------------|----------------------\nv1      | July, 2017   | (this page)\n\n# Authentication\n <!-- ReDoc-Inject: <security-definitions> --> \n\n# Pagination\nPagination is not available on this API.\n\n# Frequently Asked Question\nQ1: What is the accessToken to be used in the API headers?\n\nAns: The accessToken should be the Partner's token and not the Customer's accessToken.\n\n# Known Issues\nThis API has no pending issues at the moment. Want to report a new issue? please help us **here**\n\n# Throttling (Rate Limits)\nWe throttle our APIs by default to ensure maximum performance for all developers.\n\nBelow is more details to control API rate limits\n".format(description,title)
	headers_missing=check_overview(overview_headers,description)
	elif len(headers_missing) != 0:
		print("Sections missing: "+", ".join(headers_missing))
		input["info"]["description"]= new_description
	if input.get("schemes") == None or "https" not in input.get("schemes"):
		input["schemes"]=["https"]
		print("{}: Schemes are defined".format(title))
	if "www.dbs.com/sandbox" not in input.get("host"):
		input["host"]="www.dbs.com/sandbox"
		print("{}: Hostname is corrected".format(title))
	## Check for security definitions
	if "securityDefinitions" not in input:
		print("{}: Security definitions added, please check".format(title))
		input["securityDefinitions"]={
		"accessToken": {
			"description": "{} requires a valid clientId & partner accessToken to execute any operations. You can obtain one through the Authorization Steps. Please go through the &quot;Getting Started&quot; section for more details.\n".format(title),
			"type": "oauth2",
			"authorizationUrl": "https://www.dbs.com/sandbox/api/sg/v1/oauth/authorize",
			"tokenUrl": "https://www.dbs.com/sandbox/api/sg/v1/oauth/token",
			"flow": "accessCode",
			"scopes": {
				"Scope of access": "Description of scope"
			}
		}
	}
	
	## Get list of api methods
	apis = input.get("paths")
	for k in apis:
		api_set = apis.get(k).items()
		## Get/Post on the api path
		for methods in api_set:
			api_method, api= methods[0], methods[1]
			summary = api.get("summary")
			## Check capitalized summary
			if check_caps(summary) is False:
				api["summary"]= summary.capitalize()
				print("Method {}/{}: Summary has been capitalized.".format(k,api_method))
			if summary.startswith("get"):
				api["summary"]= summary.replace("get","Retrieve")
				print("Method {}/{}: Replaced 'get' with 'Retrieve'".format(k,api_method))
			param_list = [d['name'] for d in api.get("parameters")]
			parameters = api.get("parameters")
			## Check if parameter has in:"path", if yes its required: True
			for item in parameters:
				if item.get("in")=="path" and item.get("required")=="false":
					item["required"]="true"
					print("Method {}/{} : Path parameter corrected".format(k,api_method))
			## Check accept-version header and description
			if "accept" in param_list:
				del api["parameters"]["accept"]
				print("Method {}/{} : Wrong accept header deleted".format(k,api_method))
			if "accept-version" in param_list:
				for item in parameters:
					if item.get("name") == "accept-version":
						if item.get("description") != "Specifies the acceptable version of the message set. If not specified, the latest version of the API will be considered. Example: 1.2":
							item["description"] = "Specifies the acceptable version of the message set. If not specified, the latest version of the API will be considered. Example: 1.2"
							print("Method {}/{} : Description changed to its correct form".format(k,api_method))
				api["parameters"]= parameters
							
			else:
				accept_header={
							"name": "accept-version",
							"in": "header",
							"description": "Specifies the acceptable version of the message set. If not specified, the latest version of the API will be considered. Example: 1.2",
							"required": False,
							"type": "string"
						}
				api["parameters"].append(accept_header)
				print("Method {}/{}: Added accept-version.".format(k,api_method))
			## Check uuid 
			# if "uuid" not in parameters:
				# uuid={
                    # "name": "uuid", 
                    # "in": "header", 
                    # "description": "Message UID", 
                    # "required": true, 
                    # "type": "string"
                    # }
				# api["parameters"].append(uuid)
				# print("Method {} : Added uuid".format(k))
			responses =  api.get("responses")
			if "default" in responses:
				print("Method {}/{} : Default error response has been removed.".format(k,api_method))
				del api["responses"]["default"]
			if responses.get("500")== None or responses.get("500").get("schema")== None:
				print("Method {}/{} : Error 500 is defined with a schema".format(k,api_method))
				server_response={
							"description": "Internal Server Error",
							"schema": {
								"$ref": "#/definitions/errorList"
							}
						}
				api["responses"]["500"]=server_response
			methods= replace_at_index(methods,1,api)
		apis[k].update(api_set)
	input["paths"]=apis
	if input.get("definitions").get("errorList")==None:
		input["definitions"]["errorList"]={
            "description": "List of errors", 
            "type": "array", 
            "items": {
                "$ref": "#/definitions/error"
            }
        }
		print("{}: Error List definition added".format(title))
	print("Modification of {} done".format(title))
	return input
			

def fileopen(data):
	with open(data, mode= "r") as file_data:
		content = json.load(file_data, strict=False, object_pairs_hook=collections.OrderedDict)
	return content

def filewrite(data, input):
	with open(data, mode="w") as file_data:
		json.dump(input,file_data,indent=4)

def check_directory(dir):
	dir_contents=[]
	try:
		for filename in os.listdir(dir):
			if filename.endswith(".json"):
				filename= os.path.join(input_dir,filename)
				file_contents=fileopen(filename)
				dir_contents.append([filename,file_contents])
	except Exception as e:
		print("{} is not a valid JSON file".format(filename))
		print('Error on line {} \n'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
	return dir_contents
		
def main():
	file_list= check_directory(input_dir)
	for item in file_list:
		modified= modify(item[1])
		print("\n\n")
		try:
			pass
			filewrite(item[0],modified)
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		
	

if __name__ == '__main__':
	main()
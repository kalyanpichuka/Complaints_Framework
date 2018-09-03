#!/home/ignitelab/anaconda3/bin/python
from flask import Flask
from flask import request
from flask import jsonify
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from collections import OrderedDict
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.estimators import ParameterEstimator
from pgmpy.estimators import BayesianEstimator
from pgmpy.inference import VariableElimination

print("************************************************************************************************************")
print("**********************************LOADING THE MODEL*********************************************************")
print("************************************************************************************************************")

data = pd.read_csv("clusteredComplaintsDataSet_latest.csv")
data.__delitem__('ID')
data.__delitem__('Time Difference')
data.__delitem__('Class cluster')
data.__delitem__('Count')

model = BayesianModel([('City', 'Issue'), ('Submitted via', 'Issue'), ('Company response to consumer','Issue')])

model.fit(data, estimator=BayesianEstimator, prior_type="BDeu")

issue_inference = VariableElimination(model)

print("************************************************************************************************************")
print("**********************************COMPLETED LOADING THE MODEL***********************************************")
print("************************************************************************************************************")

city_dict = {}
submitted_via_dict = {}
company_response_dict = {}
issue_dict = {}

city_list = sorted(list(data['City'].unique()))
submitted_via_list = sorted(list(data['Submitted via'].unique()))
company_response_list = sorted(list(data['Company response to consumer'].unique()))
issue_list = sorted(list(data['Issue'].unique()))

city_count = len(city_list)
submitted_via_count = len(submitted_via_list)
company_response_count = len(company_response_list)
issue_count = len(issue_list)


i=0
for city in city_list:
  city_dict[city] = i
  i += 1

i=0
for submitted_via in submitted_via_list:
  submitted_via_dict[submitted_via] = i
  i += 1


i=0
for company_response in company_response_list:
  company_response_dict[company_response] = i
  i += 1

i=0
for issue in issue_list:
  issue_dict[issue] = i
  i += 1


#RETRIVING KEYS RELATED TO TOP MAX VALUES
def _get_max_value_keys(array,res_dict):
  result=[]
  for element in array:
    result.append([key for key, value in res_dict.items() if value == element][0])
  return result

# RETRIVING ISSUES BASED ON THE CITY,SUBMITTED VIA,COMPANY RESPONSE
def _get_issues_(city,submitted_via,company_response):
  result=[]
  prob_issue_multiple = issue_inference.query( variables = ['Issue'],evidence = {'City':city_dict[city],'Submitted via':submitted_via_dict[submitted_via],'Company response to consumer':company_response_dict[company_response]})
  result = _get_max_value_keys(prob_issue_multiple['Issue'].__dict__['values'].argsort()[-1:-4:-1],issue_dict)
  return result  

print("************************************************************************************************************")
print("**********************************SERVER STARTED WITH REQUIRED UTILITIES************************************")
print("************************************************************************************************************")


app = Flask(__name__)

empDB=[
 {
 'id':'101',
 'name':'Saravanan S',
 'title':'Technical Leader'
 },
 {
 'id':'201',
 'name':'Rajkumar P',
 'title':'Sr Software Engineer'
 }
 ]

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/display', methods=['GET'])
def getName():
    firstname = request.args.get('firstname')
    lastname = request.args.get('lastname')
    result = [{'first':firstname,'last':lastname}]
    return jsonify({'name':result})

@app.route('/maxProb', methods=['GET'])
def getMaxProb():
    city = request.args.get('city')
    sub_via = request.args.get('sub_via')
    comp_res = request.args.get('comp_res')
    prob = _get_issues_(city,sub_via,comp_res) 	
    result = [{'firstmax':prob[0],'secondmax':prob[1],'thirdmax':prob[2]}]
    return jsonify({'name':result})


@app.route('/empdb/employee',methods=['GET'])
def getAllEmp():
    return jsonify({'emps':empDB})

if __name__ == '__main__':
    app.run(debug=True)

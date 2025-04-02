from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from groq import Groq

import datetime
import json
from google import genai
import openai
from llama_index.llms.openai import OpenAI

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    file1 = request.files['data_file']
    file2 = request.files['rules_file']
    
    if not file1 or not file2:
        return jsonify({'error': 'Both files are required!'}), 400
    
    file1_path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
    file2_path = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
    file1.save(file1_path)
    file2.save(file2_path)
    sheet1=pd.ExcelFile( file1_path)

    sheetName1=sheet1.sheet_names
    df1 = pd.DataFrame() 
    for i in sheetName1:
     df1=pd.concat([df1,sheet1.parse(i)], ignore_index=False)

    result1 = [df1.columns.tolist()] + df1.values.tolist()
    result_str1 = json.dumps(result1)
    print(result_str1)


    file_data=result_str1 


    sheet=pd.ExcelFile(file2_path)

    sheetName=sheet.sheet_names

    df = pd.DataFrame() 
    for i in sheetName:
      df=pd.concat([df,sheet.parse(i)], ignore_index=False)

    result = [df.columns.tolist()] + df.values.tolist()
    result_str = json.dumps(result)
    print(result_str)
    error_data=result_str

    prompt='''
Do a data validation on a set of data  given when error data is provided . The output will be used by Data analyst for finding error in data set.  Validate the data in  file_data  with the corresponding validation  provide in error_data . 

##Instruction 
Consider the value in the 1st column in error_data as the column name in file_data and the second column in error_data is the validation which needs to performed on the corresponding column data  in file_data .Provide an output in html Table format mentioning the Validation message , column name and column value when the validation message in not satisfied.
The validation column in error_data can have multiple condition with  or/and . In case multiple condition , the validation should consider both the condtions.
Do the validation of file_data provided in input Data and  Give the output as provided in sample output.
Data in the 'User ID' and 'Prot_ID' columns are either email addresses or non-email alphanumberic string.Consider anything which ends @syf.com as the only valid email address for User_ID and Prot_id column .
Data in the email column can be any valid email address like gmail.com or yahoo.com
Do not include any sample code in the output.
Below is the  sample file_data and error_data
Sample file_data = [
    ["Name", "Age", "City"],
    ["John", "25", "New York"],
    ["Alice", "30", "Los Angeles"],
    ["Bob", "35", "Chicago"],
    ["", "25", "New York"],
    ["John", "abc", "New York"],
    ["John", "50", "New York"]
]

Sample error_data = [
    ["Name", "should not be empty or it should start with A"],
    ["Age", "should be integer"],
    ["Age", "should be within range(18,100)"],
    ["City", "should not be empty"]
]

Sample output:
        <table class="table table-striped table-bordered">
          <thead>
            <tr>
              <th>Row Number</th>
              <th>Column Name</th>
              <th>Value</th>
              <th>Validation Error</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>3</td>
              <td>Name</td>
              <td>Alice</td>
              <td>should not be empty or it should start with A</td>
            </tr>
            <tr>
              <td>5</td>
              <td>Name</td>
              <td></td>
              <td>should not be empty or it should start with A</td>
            </tr>
            <tr>
              <td>6</td>
              <td>Age</td>
              <td>abc</td>
              <td>should be integer</td>
            </tr>
            <tr>
              <td>6</td>
              <td>Age</td>
              <td>abc</td>
              <td>should be within range(18,100)</td>
            </tr>
          </tbody>
        </table>

Input Data:

file_data: input_file_data 
error_data: error_file_data '''



    prompt=prompt.replace("input_file_data",file_data)
    prompt=prompt.replace("error_file_data",error_data)


    print(prompt)
    client = genai.Client(api_key="AIzaSyCc2Cit_TfxW_R6n2wpvE4woaDIlwGV6vM")
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt
)

    
     # Return the validation results and file information
    file_info = {
            'data_file': {
                'name': file1.filename,
                'sheets': sheetName1,
                'rows': len(df1)
            },
            'rules_file': {
                'name': file2.filename,
                'sheets': sheetName,
                'rows': len(df)
            }
        }
        
    return render_template('results.html', validation_results=response.text, file_info=file_info)

@app.route('/validate', methods=['POST'])
def validate_files():
    file1_name = request.json.get('file1')
    file2_name = request.json.get('file2')
    
    file1_path = os.path.join(app.config['UPLOAD_FOLDER'], file1_name)
    file2_path = os.path.join(app.config['UPLOAD_FOLDER'], file2_name)
    
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        return jsonify({'error': 'Files not found!'}), 400
    
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)
    
    merged_df = pd.merge(df1, df2, how='outer')
    result_html = merged_df.to_html(classes='table table-bordered')
    
    return jsonify({'table': result_html})

if __name__ == '__main__':
    app.run(debug=True)

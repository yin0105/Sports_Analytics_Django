# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import os, pickle

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

@login_required(login_url="/login/")
def index(request):
    
    context = {}
    context['segment'] = 'index'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def dashboard(request, sports):
    context = {}
    try:
        sports      = request.path.split('/')[-1]

        creds = None
        sheet_id =  "1raKXpvMoze4lWoN0f-KZSEy07wrnp9f83FO2UseZKCE"
        sheet_name =  "Sheet1"
        sheet_range =  "A1:I10000"
        print("sheet range = " + sheet_range)
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                print("111")

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("112")
                    creds.refresh(Request())
                else:
                    print("113")
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    creds = flow.run_local_server(port=21000)
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                    print("114")

        print("115")                    

        service = build('sheets', 'v4', credentials=creds)
        print("116")

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_name + "!" + sheet_range).execute()
        values = result.get('values', [])
            
        resp = ""
        # resp = '<iframe src="/static/chart/' + chart_id + '.html" width="100%" height="600px"></iframe>'
        if values:
            print("OK")
            print(len(values))
        else :
            print("No value")
            # From To (Change Field Name)
            # fields = Field.query.join(Field_Type, Field.field_type==Field_Type.id).add_columns(Field.from_, Field.to, Field.rule, Field_Type.field_type).filter(Field.tbl_id==tbl_id).all()
            # print("tbl_id = " + str(tbl_id))
            # new_values = []
            # new_columns = [] # fields name list
            # index_columns = [] # indexes list
            # name_columns = {} # name mapping dictionary (field name -> virtual variable name that will be used in expression)
            # rule_columns = []
            # type_columns = []
            # col_index = -1
            # field_index = -1
            
            # for column in values[0]:
            #     col_index += 1                        
            #     for field in fields: 
            #         if col_index == 0: print("field : #" + field.to + "#")                             
            #         if field.from_ == column:
            #             field_index += 1  
            #             new_columns.append(field.to)
            #             type_columns.append(field.field_type)
            #             index_columns.append(col_index)
            #             print(column + " :: " + str(col_index))
            #             name_columns[field.to] = "a_" + str(field_index)
            #             rule_columns.append("")
            #             break
            # print("len = " + str(len(fields)))
            # col_index = -1
            # for field in fields:
            #     if not field.to in name_columns.keys():
            #         from_ = field.from_
            #         if from_.strip() == "":
            #             field_index += 1  
            #             new_columns.append(field.to)
            #             index_columns.append(col_index)
            #             name_columns[field.to] = "a_" + str(field_index)
            #             type_columns.append("")
            #             rule_columns.append(field.rule)

            # for i in range(len(new_columns)):
            #     if index_columns[i] == -1:
            #         rr = rule_columns[i]
            #         for cc in new_columns:
            #             rr = rr.replace(cc, name_columns[cc])
            #         rule_columns[i] = rr

            # new_values.append(new_columns)
            # for row in values[1:]:
            #     tmp_row = []
            #     for i in range(len(new_columns)):
            #         if type_columns[i] != "Text":
            #             print("type = " + type_columns[i])
            #             exec(str(name_columns[new_columns[i]]) + "=" + str(locale.atof(str(row[index_columns[i]]))))
            #     for i in range(len(new_columns)):
            #         if index_columns[i] > -1:
            #             tmp_row.append(row[index_columns[i]])
            #             print(str(name_columns[new_columns[i]]))                    
            #         else:
            #             print("eval :: " + str(rule_columns[i]))
            #             tmp_row.append(eval(rule_columns[i]))
            #     new_values.append(tmp_row)
            # print(new_values)
            #     # new_values.append(row)




        context['segment'] = 'dashboard.html'
        html_template = loader.get_template( 'dashboard.html' )
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))

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

import os, pickle, re

from pyasn1.type.univ import Null

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
team_data = []

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
    print("dashboard::::::::::::::::::")
    global team_data
    context = {}
    header_arr = []  
    render_data = []

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

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    creds = flow.run_local_server(port=21000)
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_name + "!" + sheet_range).execute()
        values = result.get('values', [])
            
        resp = ""
        # resp = '<iframe src="/static/chart/' + chart_id + '.html" width="100%" height="600px"></iframe>'
        if values:
            print(len(values))
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
            
            # Get Header 
            for column in values[0]:
                header_arr.append(column.lower())
            if len(values[0]) == 8 : header_arr.append("day")
            
            for row in values[1:]:
                temp_team_data = {}                
                for i in range(len(row)):
                    # print(header_arr[i])
                    if header_arr[i] == "team" and row[i].strip() == "": 
                        temp_team_data = {}
                        break
                    elif header_arr[i] == "mode":
                        mod = []
                        if row[i].lower().strip() == "no":
                            temp_team_data["mode_aver"] = 0
                        else:
                            mod = re.split(" +", row[i].replace(",", " ").strip())
                            # if temp_team_data["team"] == "Quinnipiac": print(mod)
                            mod_sum = 0
                            for mod_1 in mod:
                                mod_sum += float(mod_1)
                            mod_sum /= len(mod)
                            temp_team_data["mode_aver"] = mod_sum

                        temp_team_data["mode"] = mod
                    else:
                        temp_team_data[header_arr[i]] = row[i].strip()
                if len(temp_team_data) == 0: continue

                # Calc Total/Average
                if temp_team_data["mode_aver"] == 0:
                    temp_team_data["ta"] = (float(temp_team_data["mean/avs"]) + float(temp_team_data["median"])) / 2
                else:
                    temp_team_data["ta"] = (float(temp_team_data["mean/avs"]) + float(temp_team_data["median"]) + temp_team_data["mode_aver"]) / 3
                
                if len(team_data) < 2:
                    team_data.append(temp_team_data)
                    if len(team_data) == 2:
                        # Calc & Comp
                        temp_render_data = {}
                        temp_render_data["date"] = "2021/03/01"
                        temp_render_data["team_1"] = team_data[0]["team"]
                        temp_render_data["team_2"] = team_data[1]["team"]
                        # calc_score()
                        temp_render_data["score"] = calc_score()
                        temp_render_data["winner"] = "None"
                        render_data.append(temp_render_data)
                        team_data = []
                # for v in temp_team_data:
                #     print(len(v))
                #     print(v + " : " + temp_team_data[v])
                # print("::" + temp_team_data["team"] + "::")
        context['segment'] = 'dashboard.html'
        context['data'] = render_data
        print(len(render_data))
        html_template = loader.get_template( 'dashboard.html' )
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))


def calc_score():
    global team_data
    score = 0
    # print("calc_score() :: ")
    # print(len(team_data))
    # print(team_data[0]["mode_aver"])
    # print(team_data[1]["mode_aver"])
    # print(team_data[0]["median"])
    # print(team_data[1]["median"])
    # print(team_data[0]["mean/avs"])
    # print(team_data[1]["mean/avs"])

    if team_data[0]["mode_aver"] == 0 or team_data[1]["mode_aver"] == 0:
        score = (float(team_data[0]["mean/avs"]) + float(team_data[0]["median"]) + float(team_data[1]["mean/avs"]) + float(team_data[1]["median"])) / 2
    else:
        score = (float(team_data[0]["mean/avs"]) + float(team_data[0]["median"]) + float(team_data[0]["mode_aver"]) + float(team_data[1]["mean/avs"]) + float(team_data[1]["median"]) + float(team_data[1]["mode_aver"])) / 3
    # print(score)
    return "{:.2f}".format(score)



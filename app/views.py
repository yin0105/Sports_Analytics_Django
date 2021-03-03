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
from app.models import SportsURL

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
team_data = []
sports_urls = {}
sports_sheet = {}
sports_rule = {}
sports_victory = {}
current_sports = ""
current_page = "dashboard"

@login_required(login_url="/login/")
def index(request):
    global sports_urls, sports_sheet, current_sports, current_page, team_data
    
    context = {}
    context['segment'] = 'index'

    get_sports_data()
        
    context["sports_urls"] = sports_urls
    context["current_sports"] = current_sports
    print("current sports = " + current_sports)
    print("redirect")
    # html_template = loader.get_template( 'dashboard.html' )
    # return HttpResponse(html_template.render(context, request))
    return redirect('dashboard')


@login_required(login_url="/login/")
def set_sports(request):
    global current_sports
    current_sports = request.GET["sports"]
    return redirect(current_page)


@login_required(login_url="/login/")
def set_settings(request):
    global current_sports
    print(request.GET["team"])
    print(request.GET["sheet_id"])
    print(request.GET["sheet_name"])
    print(request.GET["rule"])
    print(request.GET["victory"])
    print(request.GET["settings_way"])

    if request.GET["settings_way"] == "update" :
        try:
            print("current_sports = " + current_sports)
            cur_sports = SportsURL.objects.get(sports=current_sports)
            cur_sports.sports = request.GET["team"]
            cur_sports.url = request.GET["sheet_id"]
            cur_sports.sheet = request.GET["sheet_name"]
            cur_sports.victory = request.GET["victory"]
            cur_sports.rule = request.GET["rule"]
            cur_sports.save()
        except:
            pass
    elif request.GET["settings_way"] == "add" :
        pass
    current_sports = ""
    get_sports_data()
    return redirect('settings')


@login_required(login_url="/login/")
def pages(request):
    global sports_urls, sports_sheet, current_sports, current_page, team_data
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
def dashboard(request):
    global sports_urls, sports_sheet, current_sports, current_page, team_data
    print("dashboard::::::::::::::::::")
    if current_sports == "": get_sports_data()
    current_page = "dashboard"
    context = {}
    header_arr = []  
    render_data = []

    try:
        creds = None
        print("1")
        print("current_sports = " + current_sports)
        # sheet_id =  "1raKXpvMoze4lWoN0f-KZSEy07wrnp9f83FO2UseZKCE"
        # sheet_id =  "1FyYgEeBucZgt3SZZremSmaCL10itggnom4XSjaA9CKw"
        sheet_id =  sports_urls[current_sports]
        
        print(sports_urls[current_sports])
        sheet_name =  sports_sheet[current_sports]
        sheet_range =  "A1:I1000"
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
        print("1")
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_name + "!" + sheet_range).execute()
        values = result.get('values', [])
        print("3")
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
            day = ""
            for row in values[1:]:
                temp_team_data = {}                
                for i in range(len(row)):
                    if i>8 : break
                    if header_arr[i] == "team" and row[i].strip() == "": 
                        temp_team_data = {}
                        break
                    elif header_arr[i] == "mode":
                        mod = []
                        if row[i].lower().strip() == "no":
                            temp_team_data["mode_aver"] = 0
                        else:
                            mod = re.split(" +", row[i].replace(",", " ").strip())
                            mod_sum = 0
                            for mod_1 in mod:
                                mod_sum += float(mod_1)
                            mod_sum /= len(mod)
                            temp_team_data["mode_aver"] = mod_sum

                        temp_team_data["mode"] = mod
                    else:
                        temp_team_data[header_arr[i]] = row[i].strip()
                    if i == 8: day = row[i].replace("-", "/")
                if len(temp_team_data) == 0: continue

                print(temp_team_data["team"])

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
                        temp_render_data["date"] = day
                        temp_render_data["team_1"] = team_data[0]["team"]
                        temp_render_data["team_2"] = team_data[1]["team"]
                        temp_render_data["score"] = calc_score()
                        temp_render_data["winner"] = decision_winner()
                        render_data.append(temp_render_data)
                        team_data = []
        context['segment'] = 'dashboard.html'
        context["sports_urls"] = sports_urls
        context["current_sports"] = current_sports
        context['data'] = render_data
        print(len(render_data))
        html_template = loader.get_template( 'dashboard.html' )
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def settings(request):
    global sports_urls, sports_sheet, sports_victory, sports_rule, current_sports, current_page, team_data
    if current_sports == "": get_sports_data()
    current_page = "settings"
    context = {}
    header_arr = []  
    render_data = []

    
    context['segment'] = 'settings.html'
    context['sheet_id'] = ''
    context['sheet_name'] = ''
    context['rule'] = ''
    context['victory'] = 0
    context['sports_urls'] = sports_urls

    if len(sports_urls) > 0 :
        context['sheet_id'] = sports_urls[current_sports]
        context['sheet_name'] = sports_sheet[current_sports]
        context['rule'] = sports_rule[current_sports]
        context['victory'] = sports_victory[current_sports]
    context["current_sports"] = current_sports
    html_template = loader.get_template( 'settings.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def calculator(request):
    global sports_urls, sports_sheet, current_sports, current_page, team_data
    context = {}
    header_arr = []  
    render_data = []

    
    context['segment'] = 'ui-typography.html'
    context["sports_urls"] = sports_urls
    context["current_sports"] = current_sports
    # context['data'] = render_data
    print(len(render_data))
    html_template = loader.get_template( 'ui-typography.html' )
    return HttpResponse(html_template.render(context, request))
    

def calc_score():
    global team_data
    score = 0

    if team_data[0]["mode_aver"] == 0 or team_data[1]["mode_aver"] == 0:
        score = (float(team_data[0]["mean/avs"]) + float(team_data[0]["median"]) + float(team_data[1]["mean/avs"]) + float(team_data[1]["median"])) / 2
    else:
        score = (float(team_data[0]["mean/avs"]) + float(team_data[0]["median"]) + float(team_data[0]["mode_aver"]) + float(team_data[1]["mean/avs"]) + float(team_data[1]["median"]) + float(team_data[1]["mode_aver"])) / 3
    # print(score)
    return "{:.2f}".format(score)


def decision_winner():
    global team_data
    if float(team_data[0]["variance"]) > float(team_data[1]["variance"]) and team_data[0]["ta"] > team_data[1]["ta"]:
        return team_data[0]["team"]
    elif float(team_data[1]["variance"]) > float(team_data[0]["variance"]) and team_data[1]["ta"] > team_data[0]["ta"]:
        return team_data[1]["team"]
    else:
        return ""


def get_sports_data():
    global sports_urls, sports_sheet, current_sports
    sports_urls_tmp = SportsURL.objects.all()
    sports_urls.clear()
    for sports in sports_urls_tmp:
        if current_sports == "": current_sports = sports.sports
        sports_urls[sports.sports] = sports.url
        sports_sheet[sports.sports] = sports.sheet
        sports_rule[sports.sports] = sports.rule
        sports_victory[sports.sports] = sports.victory


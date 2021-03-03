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

import os, pickle, re, math

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
        try:
            cur_sports = SportsURL(sports = request.GET["team"], url = request.GET["sheet_id"], sheet = request.GET["sheet_name"], victory = request.GET["victory"], rule = request.GET["rule"])
            cur_sports.save()
        except:
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
                        # Calc
                        calc_data = [(float(team_data[0]["mean/avs"]) + float(team_data[1]["mean/avs"])) / 2, (float(team_data[0]["median"]) + float(team_data[1]["median"])) / 2, (float(team_data[0]["mode_aver"]) + float(team_data[1]["mode_aver"])) / 2, (float(team_data[0]["ta"]) + float(team_data[1]["ta"])) / 2]
                        c_mode = calc_mode(calc_data)
                        c_mean = calc_mean(calc_data)
                        c_median = calc_median(calc_data)
                        if len(c_mode) == 0:
                            c_score = (c_mean + c_median) / 2
                        else:
                            c_score = (c_mean + c_median + calc_mean(c_mode)) / 3
                        temp_render_data = {}
                        temp_render_data["date"] = day
                        temp_render_data["team_1"] = team_data[0]["team"]
                        temp_render_data["team_2"] = team_data[1]["team"]
                        temp_render_data["score_1"] = "{:.2f}".format(team_data[0]["ta"])
                        temp_render_data["score_2"] = "{:.2f}".format(team_data[1]["ta"])
                        temp_render_data["score"] = "{:.2f}".format(c_score)
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
    resp = [] 
    req = ""   
    # label_arr = ["Population size:", "Mean (μ):", "Median:", "Mode:", "Lowest value:", "Highest value:", "Range:", "Interquartile range:", "First quartile:", "Third quartile:", "Variance (σ2):", "Standard deviation (σ):", "Quartile deviation:", "Mean absolute deviation (MAD):"]

    if "data" in request.GET :
        que_str = re.split(" +", request.GET["data"].replace(",", " ").strip())
        que = []      
        req = request.GET["data"]  
        try :
            for q in que_str:
                que.append(float(q))
            # Population size
            resp.append({"label":"Population size:", "val":len(que)})
            # Mean (μ)
            resp.append({"label":"Mean (μ):", "val":calc_mean(que)})
            # Median
            resp.append({"label":"Median:", "val":calc_median(que)})
            # Mode
            print(calc_mode(que))
            temp = ', '.join([str(i) for i in calc_mode(que)])
            print(temp)
            if temp == "": temp = "No"
            resp.append({"label":"Mode:", "val":temp})
            # Lowest value
            resp.append({"label":"Lowest value:", "val":calc_lowest(que)})
            # Highest value
            resp.append({"label":"Highest value:", "val":calc_highest(que)})
            # Range
            resp.append({"label":"Range:", "val":calc_range(que)})
            # Interquartile range
            resp.append({"label":"Interquartile range:", "val":calc_inter_q(que)})
            # First quartile
            resp.append({"label":"First quartile:", "val":calc_first_q(que)})
            # Third quartile
            resp.append({"label":"Third quartile:", "val":calc_third_q(que)})
            # Variance (σ2)
            resp.append({"label":"Variance (σ2):", "val":calc_variance(que)})
            # Standard deviation (σ)
            resp.append({"label":"Standard deviation (σ):", "val":calc_sd(que)})
            # Quartile deviation
            resp.append({"label":"Quartile deviation:", "val":calc_qv(que)})
            # Mean absolute deviation (MAD)
            resp.append({"label":"Mean absolute deviation (MAD):", "val":calc_mad(que)})
        except :
            pass
    if len(resp) < 14 :
        print("except" + str(len(resp)))
        resp.clear()
        resp.append({"label":"Population size:", "val":""})
        resp.append({"label":"Mean (μ):", "val":""})
        resp.append({"label":"Median:", "val":""})
        resp.append({"label":"Mode:", "val":""})
        resp.append({"label":"Lowest value:", "val":""})
        resp.append({"label":"Highest value:", "val":""})
        resp.append({"label":"Range:", "val":""})
        resp.append({"label":"Interquartile range:", "val":""})
        resp.append({"label":"First quartile:", "val":""})
        resp.append({"label":"Third quartile:", "val":""})
        resp.append({"label":"Variance (σ2):", "val":""})
        resp.append({"label":"Standard deviation (σ):", "val":""})
        resp.append({"label":"Quartile deviation:", "val":""})
        resp.append({"label":"Mean absolute deviation (MAD):", "val":""})
        
    
    context['segment'] = 'calculator.html'
    context["resp"] = resp
    context["req"] = req
    print("$"*50)
    print(len(resp))
    html_template = loader.get_template( 'calculator.html' )
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


def calc_mean(que):
    s = 0
    for q in que:
        s += q
    return s/len(que)


def calc_median(que):
    que.sort()
    n = len(que)
    print("n = " + str(n))
    print(que)
    if n % 2 == 0:
        return (que[n//2-1] + que[n//2]) / 2
    else:
        return que[(n-1)//2]


def calc_mode(que):
    que.sort()
    res_que = []
    pre_q = que[0]
    repeat_count = 1
    max_repeat_count = 2
    for q in que[1:]:
        if pre_q == q:
            repeat_count += 1
        else:
            if repeat_count == max_repeat_count :
                res_que.append(pre_q)
            elif repeat_count > max_repeat_count :
                max_repeat_count = repeat_count
                res_que.clear()
                res_que.append(pre_q)
            repeat_count = 1
            pre_q = q
    
    return res_que


def calc_lowest(que):
    que.sort()
    return que[0]


def calc_highest(que):
    que.sort()
    return que[-1]


def calc_range(que):
    que.sort()
    return que[-1] - que[0]


def calc_inter_q(que):
    if len(que) < 4:
        return "N/A"
    return calc_third_q(que) - calc_first_q(que)

def calc_first_q(que):
    if len(que) < 4:
        return "N/A"
    que.sort()
    n = len(que)
    if (n+1) % 4 == 0:
        return que[(n+1)//4 - 1]
    return que[(n+1)//4 - 1] + (que[(n+1)//4] - que[(n+1)//4 - 1]) * ((n+1)/4 - (n+1)//4)


def calc_third_q(que):
    if len(que) < 4:
        return "N/A"
    que.sort()
    n = len(que)
    if (n+1) % 4 == 0:
        return que[(n+1) // 4 * 3 - 1]
    return que[(n+1)//4*3 - 1] + (que[(n+1)//4*3] - que[(n+1)//4*3 - 1]) * ((n+1)/4*3 - (n+1)//4*3)


def calc_variance(que):
    mean = calc_mean(que)
    s = 0
    for q in que:
        s += (q - mean) ** 2
    s = s / ( len(que) - 1 )
    return s


def calc_sd(que):
    return math.sqrt(calc_variance(que))


def calc_qv(que):
    if len(que) < 4:
        return "N/A"
    return calc_inter_q(que) / 2


def calc_mad(que): 
    print("calc_mad")
    mean = calc_mean(que)
    print(mean)
    que_2 = [abs(q - mean) for q in que]                                      
    print(que_2)
    return calc_mean(que_2)
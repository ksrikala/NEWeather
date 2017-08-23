from django.http import HttpResponse,HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render_to_response
from django.template import loader
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from necloudweather.models import *
from  cloudweather.models import *
import pymongo,re, datetime, collections, json
from pymongo import MongoClient
from json import loads,dumps
from datetime import date, timedelta
#@login_required
from django.core.cache import cache
cache_time = 1800
import sys
def index(request):
    print 'coming here',request.user,request.user.is_authenticated()
    regions=aws_regions()
    services=aws_services()
    context = {'regions':regions,'services':services}
    if request.user.is_authenticated():
        print 'oops'
        context['user'] = request.user.username
    else:
        context['user'] = 'no_user'
    return render(request, "homepage.html", context)
def results(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/') 
    environment = request.POST.get('environment')
    if "search_id" in request.POST:
        ids = request.POST["search_id"]
        s = SavedFilter.objects.filter(id=ids)[0]
        services = eval(s.services)
        regions = eval(s.regions)
        from_date = s.date1
        to_date = s.date2
	date=daterange(from_date,to_date)
    else:
        services = request.POST.getlist('services')
        #services = [x.encode('UTF8') for x in services]
        from_date = request.POST['fromdate']
        to_date = request.POST['todate']
        date=daterange(from_date,to_date)
        regions = request.POST.getlist('regions')
        #dc = [x.encode('UTF8') for x in regions];
    if 'saveorrun' in request.POST and request.POST['saveorrun'] == "1":
        s1 = SavedFilter.objects.filter(user=request.user,templatename=request.POST.get('templatename'),cloudprovider=environment,regions = str(regions), services = str(services),date1 = from_date, date2=to_date)
        if len(s1) == 0:
            s = SavedFilter(user=request.user,templatename=request.POST.get('templatename'),cloudprovider=environment,regions = str(regions), services = str(services),date1 = from_date,date2=to_date )
            s.save()
    if str(environment) == 'AWS':
        results=aws_results(regions,services,date)
        regions=aws_regions()
        services=aws_services() 
    elif str(environment) == 'Azure':
        results=azure_results(regions,services,date)
        regions=azure_dc()
        services=azure_services()
    elif str(environment) == 'Google':
        results=google_results(regions,services,date)
        regions=google_regions()
        services=google_services()

    return render(request, "resultspage.html", {'regions':aws_regions(),'services':aws_services(),'results':results,'dates':date})
def registration(request):
        return render(request, "registration.htm")

def daterange(f , t):
        print f
        if f == '' and t== '':
	        today = datetime.date.today()
                f = today - datetime.timedelta(days=1)
                t=today
    	else :
    		f=datetime.datetime.strptime(f.encode('utf-8'), '%m/%d/%Y')
    		t=datetime.datetime.strptime(t.encode('utf-8'), '%m/%d/%Y')
	delta = t-f
        datelist=[]
	for i in range(delta.days + 1):
		l= (f + timedelta(days=i))
		datelist.append(l.strftime('%b %d %Y'))
        return datelist
def post1(request):
    environment = request.POST.get('env')
    if str(environment) == "AWS":
        regions = aws_regions()
        services = aws_services()
    elif str(environment) == "Azure":
        regions = azure_dc()
        services = azure_services()  
    elif str(environment) == "Google":
        regions = google_regions()
        services = google_services()
    data = json.dumps({'reg': regions,'ser': services})
    return HttpResponse(json.dumps(data), content_type="application/json")
def azure_dc():
    cache_key = "azureasia"
    azureasia = cache.get(cache_key)
    print azureasia
    if not azureasia:
	print "ji"
        azureasia=azure_asia.objects.all()
	print sys.getsizeof(azureasia)
        r=cache.set(cache_key,azureasia, cache_time)
    	print r
    cache_key = "azureamericas"
    azureamericas = cache.get(cache_key)
    if not azureamericas:
	print "america"
        azureamericas=azure_americas.objects.all()
        cache.set(cache_key, azureamericas, cache_time)
    cache_key = "azureeurope"
    azureeurope = cache.get(cache_key)
    if not azureeurope:
	print "eu"
        azureeurope=azure_europe.objects.all()
        cache.set(cache_key, azureeurope, cache_time)
    all_data=[azureasia,azureamericas,azureeurope]
    dc_list =[]
    for i in all_data:
        for j in i:
		temp=re.findall(r"\([\w\s\p{~`!@#$%^|&:;.,'*}]*\)",str(j.service))
        	if temp:
                	dc_list.append(temp[-1])
    azure_dc_list=[]
    for i in dc_list:
        azure_dc_list.append(str(i)[1:-1])
    azure_dc_list.sort()
    return list(set(azure_dc_list))
def azure_services():
    cache_key = "azureamericas"
    azureamericas = cache.get(cache_key)
    if not azureamericas:
        azureamericas=azure_americas.objects.all()
        cache.set(cache_key, azureamericas, cache_time)
    all_data=[azureamericas]
    all_services=azure_dc()
    string=""
    service_list =[]
    azure_service_list=[]
    for i in all_data:
        for j in i:
            for k in all_services:
                substring='('+str(k)+')'
                if substring in str(j.service):
                    service_list.append(re.sub(substring,'',str(j.service))[:-3])

    for i in list(set(service_list)):
        if i[-1:] != " ":
            azure_service_list.append(i)
    azure_service_list.sort()
    return azure_service_list 
def azure_results(region,service,dates):
    services = [x.encode('UTF8') for x in service] 
    regions = [x.encode('UTF8') for x in region];
    d={}
    for i in services:
        rz={}
        for j in regions:
            dt=[]
            for k in dates:
                n={}
                flag=1
                if flag:
                    try:
                        asia=azure_asia.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    except azure_asia.DoesNotExist:
                        asia=0
                    if asia:                        
                        n['date']=asia.date
                        n['status']=asia.status
                        flag=0
                if flag:
                    try:
                        america=azure_americas.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    except azure_americas.DoesNotExist:
                        america=0
                    if america:
                        n['date']=america.date
                        n['status']=america.status
                        flag=0
                if flag:
                    try:
                        europe=azure_europe.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    except azure_europe.DoesNotExist:
                        europe =0
                    if europe:
                        n['date']=europe.date
                        n['status']=europe.status
                dt.append(n)
            rz[j]= dt
        d[i]= rz
    return d
def aws_regions():
    cache_key = "awsna"
    awsna = cache.get(cache_key)
    if not awsna:
	awsna=aws_na.objects.all()
	cache.set(cache_key, awsna, cache_time)
    cache_key = "awssa"
    awssa = cache.get(cache_key)
    if not awssa:
        awssa=aws_sa.objects.all()
        cache.set(cache_key, awssa, cache_time)
    cache_key = "awseu"
    awseu = cache.get(cache_key)
    if not awseu:
        awseu=aws_eu.objects.all()
        cache.set(cache_key, awseu, cache_time)
    cache_key = "awsap"
    awsap = cache.get(cache_key)
    if not awsap:
        awsap=aws_ap.objects.all()
        cache.set(cache_key, awsap, cache_time)
    all_data=[awsna,awssa,awseu,awsap]
    dc_list =[]
    for i in all_data:
        for j in i:
        	temp=re.findall(r"\([\w\s\p{~`!@#$%^|&:;.,'*}]*\)",str(j.service))
        	if temp:
                	dc_list.append(temp[-1])
    dc_list1=[]
    for i in dc_list:
    	dc_list1.append(str(i)[1:-1])
    dc_list1.sort()
    return list(set(dc_list1))
def aws_services():
    cache_key = "awsna"
    awsna = cache.get(cache_key)
    print awsna
    if not awsna:
        awsna=aws_na.objects.all()
        cache.set(cache_key, awsna, cache_time)
    cache_key = "awssa"
    awssa = cache.get(cache_key)
    if not awssa:
        awssa=aws_sa.objects.all()
        cache.set(cache_key, awssa, cache_time)
    cache_key = "awseu"
    awseu = cache.get(cache_key)
    if not awseu:
        awseu=aws_eu.objects.all()
        cache.set(cache_key, awseu, cache_time)
    cache_key = "awsap"
    awsap = cache.get(cache_key)
    if not awsap:
        awsap=aws_ap.objects.all()
        cache.set(cache_key, awsap, cache_time)
    all_data=[awsna,awssa,awseu,awsap]
    all_regions=aws_regions()
    string=""
    service_list =[]
    aws_service_list=[]
    for i in all_data:
        for j in i:
            for k in all_regions:
                substring='('+str(k)+')'
                if substring in str(j.service):
                    service_list.append(re.sub(substring,'',str(j.service))[:-3])

    for i in list(set(service_list)):
        if i[-1:] != " ":
            aws_service_list.append(i)
    aws_service_list.sort()
    return aws_service_list
def aws_results(region,service,dates):
    services = [x.encode('UTF8') for x in service]
    regions = [x.encode('UTF8') for x in region];
    d={}
    for i in services:
        rz={}
        for j in regions:
            dt=[]
            for k in dates:
                n={}
                flag=1
                if flag:
                    try:
                        na=aws_na.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    except aws_na.DoesNotExist:
                        na=0
                    if na:
                        n['date']=na.date
                        n['status']=na.status
                        flag=0
                if flag:
                    try:
                        sa=aws_sa.objects.get(date=str(k),service=str(i +' ('+j+')'))   
                    except aws_sa.DoesNotExist:
                        sa =0
                    if sa:
                        n['date']=sa.date
                        n['status']=sa.status
                        flag=0
                if flag:
                    try:   
                        europe=aws_eu.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    except aws_eu.DoesNotExist:
                        europe=0
                    if europe:
                        n['date']=europe.date
                        n['status']=europe.status
                        flag=0
                if flag:
                    try:
                        ap=aws_ap.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    except aws_ap.DoesNotExist:
                        ap=0
                    if ap:
                        n['date']=ap.date
                        n['status']=ap.status
                        flag=0
                dt.append(n)
            rz[j]= dt
        d[i]= rz
    return d


def google_regions():
    cache_key = "googleap"
    googleap = cache.get(cache_key)
    print googleap
    if not googleap:
	print "ap"
        googleap=google_asiapacific.objects.all()
        cache.set(cache_key, googleap, cache_time)
    cache_key = "googleusa"
    googleusa = cache.get(cache_key)
    if not googleusa:
	print "usa"
        googleusa=google_americas.objects.all()
        cache.set(cache_key, googleusa, cache_time)
    cache_key = "googleeu"
    googleeu = cache.get(cache_key)
    if not googleeu:
	print "eu"
        googleeu=google_europe.objects.all()
        cache.set(cache_key, googleeu, cache_time)
    all_data=[googleap,googleusa,googleeu]
    dc_list =[]
    for i in all_data:
        for j in i:
    		temp=re.findall(r"\([\w\s\p{~`!@#$%^|&:;.,'*}]*\)",str(j.service))
        	if temp:
                	dc_list.append(temp[-1])
    dc_list1=[]
    for i in dc_list:
    	dc_list1.append(str(i)[1:-1])
    dc_list1.sort()
    return list(set(dc_list1))
def google_services():
    cache_key = "googleap"
    googleap = cache.get(cache_key)
    if not googleap:
        googleap=google_asiapacific.objects.all()
        cache.set(cache_key, googleap, cache_time)
    cache_key = "googleusa"
    googleusa = cache.get(cache_key)
    if not googleusa:
        googleusa=google_americas.objects.all()
        cache.set(cache_key, googleusa, cache_time)
    cache_key = "googleeu"
    googleeu = cache.get(cache_key)
    if not googleeu:
    	googleeu=google_europe.objects.all()
        cache.set(cache_key, googleeu, cache_time)
    all_data=[googleap,googleusa,googleeu]
    all_regions=google_regions()
    string=""
    service_list =[]
    google_service_list=[]
    for i in all_data:
        for j in i:
            for k in all_regions:
                substring='('+str(k)+')'
                if substring in str(j.service):
                    service_list.append(re.sub(substring,'',str(j.service))[:-3])

    for i in list(set(service_list)):
        if i[-1:] != " ":
            google_service_list.append(i)
    google_service_list.sort()
    return google_service_list

def google_results(region,service,dates):
    services = [x.encode('UTF8') for x in service]
    regions = [x.encode('UTF8') for x in region];
    d={}
    for i in services:
        rz={}
        for j in regions:
            dt=[]
            for k in dates:
                n={}
                flag=1
                if flag:
                    try:
                        usa=google_americas.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    except azure_europe.DoesNotExist:
                        usa=0
                    if len(usa):
                        n['date']=usa.date
                        n['status']=usa.status
                        flag=0
                if flag:
                    try:
                        ap=google_asiapacific.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    except google_asiapacific.DoesNotExist:
                        ap=0
                    if len(ap):                    
                        n['date']=ap.date
                        n['status']=ap.status
                        flag=0
                if flag:
                    try:
                        europe=google_europe.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    except google_europe.DoesNotExist:
                        europe=0
                    if len(europe):
                        n['date']=europe.date
                        n['status']=europe.status
                        flag=0
                dt.append(n)
            rz[j]= dt
        d[i]= rz
    return d

def loadregion(request):
    region = request.GET.get('region')
    environment=re.findall('\(.+\)',region)[0][1:-1]
    if environment == "AWS":
        aws_all_regions=aws_regions()
        services=aws_services()
        for i in aws_all_regions:
            if (i.replace(" ", "")+"(AWS)")==region:
                date=daterange('','')
                regions=[i]
                results=aws_results([i],services,date)
    elif environment == "Azure":
        azure_regions=azure_dc()
        services=azure_services()
        for i in azure_regions:
            if (i.replace(" ", "")+"(Azure)")==region:
                date=daterange('','')
                results=azure_results([i],services,date)
    elif environment == "Google":
        g_regions=google_regions()
        services=google_services()
        for i in g_regions:
            if (i.replace(" ", "")+"(Google)")==region:
                date=daterange('','')
                results=google_results([i],services,date)
    return render(request, "resultspage.html", {'regions':aws_regions(),'services':aws_services(),'results':results,'dates':date})
def profilerun(request):
    environment = request.POST.get('environment')
    services = request.POST.getlist('services')
    from_date = request.POST.get('fromdate')
    to_date = request.POST.get('todate')
    regions = request.POST.getlist('regions')
    services =  [str(x)[:-1] for x in services]
    regions =  [str(x)[:-1] for x in regions]
    date=daterange(from_date,to_date)
    if str(environment) == "AWS":
        results=aws_results(regions,services,date)
        regions=aws_regions()
        services=aws_services()    
    elif str(environment) == "Azure":
        results=azure_results(regions,services,date)
        regions=azure_dc()
        services=azure_services()
    elif str(environment) == "Google":
        results=aws_results(regions,services,date)
        regions=google_regions()
        services=google_services()
    return render(request, "resultspage.html", {'regions':aws_regions(),'services':aws_services(),'results':results,'dates':date})  

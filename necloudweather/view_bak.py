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
import pymongo
import re
from pymongo import MongoClient
from json import loads,dumps
from datetime import date, timedelta
import datetime
import json
import collections
mongo_server = "mongodb://13.126.3.39:27017"
client = MongoClient( mongo_server )
geo_regions = ['NA', 'SA', 'AP', 'EU' ]

#connection to database
db = client['amazon']
collections = db.collection_names()
ser = []
reg = []
data={}
datelist = []
maindc=[]
mainser=[]
#@login_required
def index(request):
    print 'coming here',request.user,request.user.is_authenticated()
    for i in range(len(geo_regions)):
        collection = db[geo_regions[i]]
        a = collection.find({}, {"service": 1})

        for row in a:
            k = row["service"].split('(')

            try:
                v = k[1].split(')')[0].encode('ascii', 'ignore')
                reg.append(v)

            except IndexError:
                no_data = "null"
    dc = list(sorted(set(reg)))
    for i in range(len(geo_regions)):
        collection1 = db[geo_regions[i]]
        b= collection1.find({}, {"service": 1})

        for row in b:
            j = row["service"].split('(')[0].encode('ascii','ignore')
            ser.append(j)
  
    s1 = list(sorted(set(ser)))
    context = {'dc':dc,'s':s1}
    print type(dc),type(s1)
    maindc=dc
    mainser=s1
    if request.user.is_authenticated():
        print 'oops'
        context['user'] = request.user.username
    else:
        context['user'] = 'no_user'
    return render(request, "cloup1.html", context)

def return_data(request):
    print maindc,'ddd',mainser
    print request.POST.getlist('regions')
    print "----------"
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/') 
    environment = request.POST.getlist('environment')
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
        services = [x.encode('UTF8') for x in services]
        from_date = request.POST['fromdate']
        to_date = request.POST['todate']
        date=daterange(from_date,to_date)
        services= [x[:-1] for x in services]
        regions = request.POST.getlist('regions')
    dc = [x.encode('UTF8') for x in regions];

    if 'saveorrun' in request.POST and request.POST['saveorrun'] == "1":
        s1 = SavedFilter.objects.filter(user=request.user,regions = str(regions), services = str(services),date1 = from_date, date2=to_date)
        if len(s1) == 0:
            s = SavedFilter(user=request.user,regions = str(regions), services = str(services),date1 = from_date,date2=to_date )
            s.save()
            messages.success(request, 'Filter Saved')
    #if "search_id" in request.POST:
    #    ids = request.POST["search_id"]print ids,'comjsfk'
    #   s = SavedFilter.objects.filter(id=ids)[0]
    #    services = eval(s.services)
    #    regions = eval(s.regions)
    #    from_date = s.date1to_date = s.date2
    all=[]
    all1={}

    for i in range(len(dc)):
        dc_finder(dc[i])
        collection = db[geo_region]

        for j in range(len(services)):
            service = services[j] + " " + '(' + dc[i] + ')'
            for d in range(len(date)):
              k = collection.find({"service": service, "date": date[d]})
              data[dc[i]]={}
              ab= dc[i]
              bc=services[j]
              abc=[]
              for row in k:
                abc.append(row)
                data[ab][bc] = row
              all.append(abc)
    ss = {}
    for d in all:
        for i in d:
            rgn = re.findall('\(.+\)',i['service'])
            if len(rgn)>0:
                rgn = rgn[0]
            else:
                rgn = 'no-region'
            sname = i['service'].replace(rgn,'')
            rgn = rgn.replace('(','')
            rgn = rgn.replace(')','')
            if sname in ss:
                if rgn in ss[sname]:
                    ss[sname][rgn].append(i)
                else:
                    ss[sname][rgn] = [i]
            else:
                ss[sname] = { rgn : [i] }
    ii=data1()
    print ss
    #return render(request, "cloup2.html", {'s':ii[1], 'dc': ii[0],'data':all, 'formatted':ss})
    return render(request,"azure.html",{'data':ss})

def dc_finder(datacenter):
    for i in range(len(geo_regions)):
        collection = db[geo_regions[i]]
        a = collection.find({}, {"service": 1})

        for row in a:
            k = row["service"].split('(')

            try:
                v = k[1].split(')')[0].encode('ascii', 'ignore')
                if v == datacenter:
                    global geo_region
                    geo_region = geo_regions[i]
                    break
            except IndexError:
                no_data = "null"

def registration(request):
        return render(request, "registration.htm")

def daterange(f , t):
        print f
        if f == '' and t== '':
	        today = datetime.date.today()
                f = today - datetime.timedelta(days=0)
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
def data1():
    dc=[]
    s1=[]
    for i in range(len(geo_regions)):
        collection = db[geo_regions[i]]
        a = collection.find({}, {"service": 1})

        for row in a:
            k = row["service"].split('(')

            try:
                v = k[1].split(')')[0].encode('ascii', 'ignore')
                reg.append(v)

            except IndexError:
                no_data = "null"
    dc = list(sorted(set(reg)))
    for i in range(len(geo_regions)):
        collection1 = db[geo_regions[i]]
        b= collection1.find({}, {"service": 1})

        for row in b:
            j = row["service"].split('(')[0].encode('ascii','ignore')
            ser.append(j)

    s1 = list(sorted(set(ser)))
    return dc,s1
def return_data1(request):
    environment = request.POST.getlist('environment')
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/') 
    else:
        services = request.POST.getlist('services')
        services = [x.encode('UTF8') for x in services]
        print services
        from_date = request.POST['fromdate']
        to_date = request.POST['todate']
        date=daterange(from_date,to_date)
        regions = request.POST.getlist('regions')
        dc = [x.encode('UTF8') for x in regions]
    for i in services:
        services = eval(i)
    for i in dc:
        dc = eval(i) 

    if 'saveorrun' in request.POST and request.POST['saveorrun'] == "1":
        s1 = SavedFilter.objects.filter(user=request.user,regions = str(regions), services = str(services),date1 = from_date, date2=to_date)
        if len(s1) == 0:
            s = SavedFilter(user=request.user,regions = str(regions), services = str(services),date1 = from_date,date2=to_date )
            s.save()
            messages.success(request, 'Filter Saved')
    all=[]
    all1={}

    for i in range(len(dc)):
        dc_finder(dc[i])
        collection = db[geo_region]

        for j in range(len(services)):
            service = services[j] + " " + '(' + dc[i] + ')'
            for d in range(len(date)):
              k = collection.find({"service": service, "date": date[d]})
              data[dc[i]]={}
              ab= dc[i]
              bc=services[j]
              abc=[]
              for row in k:
                abc.append(row)
                data[ab][bc] = row
              all.append(abc)
    ss = {}
    for d in all:
        for i in d:
            rgn = re.findall('\(.+\)',i['service'])
            if len(rgn)>0:
                rgn = rgn[0]
            else:
                rgn = 'no-region'
            sname = i['service'].replace(rgn,'')
            rgn = rgn.replace('(','')
            rgn = rgn.replace(')','')
            if sname in ss:
                if rgn in ss[sname]:
                    ss[sname][rgn].append(i)
                else:
                    ss[sname][rgn] = [i]
            else:
                ss[sname] = { rgn : [i] }
    ii=data1()
    return render(request, "cloup2.html", {'s':ii[1], 'dc': ii[0],'data':all, 'formatted':ss})


def post1(request):
    environment = request.POST.get('env')
    if environment == "AWS":
        ii=data1()
        regions = ii[0]
        services = ii[1]
    if environment == "Azure":
        regions = azure_dc()
        services = azure_services()  
    if environment == "Google":
        regions = ['Council Bluffs, Iowa, USA', 'The Dalles, Oregon', 'Ashburn, Virginia', 'Moncks Corner, South Carolina, USA', 'St. Ghislain, Belgium', 'London, U.K.', 'Jurong West, Singapore', 'Changhua County, Taiwan', 'Tokyo, Japan', 'Sydney, Australia']
        services = ['Google Compute Engine', 'Google App Engine', 'Google Cloud Bigtable', 'Google BigQuery', 'Google Cloud Functions', 'Google Cloud Datastore', 'Google Storage']
    data = json.dumps({'reg': regions,'ser': services})
    return HttpResponse(json.dumps(data), content_type="application/json")

def regions_data(request,region_name):
    if region_name == "N.Virginia":
        region_name = "N. Virginia"
    if region_name == "N.California":
        region_name = "N. California"
    if region_name == "SaoPaulo":
        region_name = "Sao Paulo"
    reg=[region_name]
    print type(reg)
    dc =[x.encode('UTF8') for x in reg]
    ii=data1()
    services=ii[1]
    services= [x[:-1] for x in services]
    from_date=''
    to_date = ''
    date=daterange(from_date,to_date)
    print date
    all=[]
    all1={}
    for i in range(len(dc)):
        dc_finder(dc[i])
        collection = db[geo_region]

        for j in range(len(services)):
            service = services[j] + " " + '(' + dc[i] + ')'
            for d in range(len(date)):
              k = collection.find({"service": service, "date": date[d]})
              data[dc[i]]={}
              ab= dc[i]
              bc=services[j]
              abc=[]
              for row in k:
                abc.append(row)
                data[ab][bc] = row
              all.append(abc)
    ss = {}
    for d in all:
        for i in d:
            rgn = re.findall('\(.+\)',i['service'])
            if len(rgn)>0:
                rgn = rgn[0]
            else:
                rgn = 'no-region'
            sname = i['service'].replace(rgn,'')
            rgn = rgn.replace('(','')
            rgn = rgn.replace(')','')
            if sname in ss:
                if rgn in ss[sname]:
                    ss[sname][rgn].append(i)
                else:
                    ss[sname][rgn] = [i]
            else:
                ss[sname] = { rgn : [i] }
    ii=data1()
    return render(request, "cloup2.html", {'s':ii[1], 'dc': ii[0],'data':all, 'formatted':ss})
def azure_dc():
    azureasia=azure_asia.objects.all()
    azureamericas=azure_americas.objects.all()
    azureeurope=azure_europe.objects.all()
    all_data=[azureasia,azureamericas,azureeurope]
    dc_list =[]
    for i in all_data:
        for j in i:
            if "(XAML)" in str(j.service):
                pass
            else:
                dc_list.append(re.findall('\(.+\)',j.service))
    azure_dc_list=[]
    for i in dc_list:
        azure_dc_list.append(str(i[0][1:-1]))
    azure_dc_list.sort()
    return list(set(azure_dc_list))
def azure_services():
    azureamericas=azure_americas.objects.all()
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
def azure(request):
    '''
    from_date = request.POST['fromdate']
    to_date = request.POST['todate']
    dates=daterange(from_date,to_date)
    print dates
    services = request.POST.getlist('services')
    services = [x.encode('UTF8') for x in services] 
    region = request.POST.getlist('regions')
    regions = [x.encode('UTF8') for x in region];
    print regions
    print services
    ''' 
    dates=["Jul 18 2017","Jul 19 2017"]
    services = ['Redis Cache', 'Recommendations API']
    regions=['West US 2','West US','West India','UK West']
    d={}
    for i in services:
        rz={}
        for j in regions:
            dt=[]
            for k in dates:
                n={}
                if len(azure_asia.objects.filter(date=str(k),service=str(i +' ('+j+')'))):
                    asia=azure_asia.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    n['date']=asia.date
                    n['status']=asia.status
                elif len(azure_americas.objects.filter(date=str(k),service=str(i +' ('+j+')'))):
                    america=azure_americas.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    n['date']=america.date
                    n['status']=america.status
                elif len(azure_europe.objects.filter(date=str(k),service=str(i +' ('+j+')'))):
                    europe=azure_europe.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    n['date']=europe.date
                    n['status']=europe.status
                dt.append(n)
            rz[j]= dt
        d[i]= rz
    print dates
    return render(request, "cloup3.html", {'data':d,'date':dates})
def aws_regions():
    awsna=aws_na.objects.all()
    awssa=aws_sa.objects.all()
    awseu=aws_eu.objects.all()
    awsap=aws_ap.objects.all()
    all_data=[awsna,awssa,awseu,awsap]
    dc_list =[]
    for i in all_data:
        for j in i:
            if "(DAX)" in str(j.service):
                pass
            else:
                dc_list.append(re.findall('\(.+\)',j.service))
    dc_list1=[]
    for i in dc_list:
        for j in i:
            dc_list1.append(str(j)[1:-1])
    dc_list1.sort()
    return list(set(dc_list1))
def aws_services():
    awsna=aws_na.objects.all()
    awssa=aws_sa.objects.all()
    awseu=aws_eu.objects.all()
    awsap=aws_ap.objects.all()
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
def aws(request):
    #from_date = request.POST['fromdate']
    #to_date = request.POST['todate']
    #dates=daterange(from_date,to_date)
    #print dates
    #services = request.POST.getlist('services')
    #services = [x.encode('UTF8') for x in services] 
    #region = request.POST.getlist('regions')
    #regions = [x.encode('UTF8') for x in region];
    #print regions
    #print services 
    dates=["Jul 06 2017","Jul 08 2017","Jun 22 2017"]
    services = ['S3', 'VPC','AWS Batch','AWS CodeStar','AWS Mobile Hub','Amazon CloudWatch']
    regions=['Frankfurt','Ireland','N. Virginia']
    d={}
    for i in services:
        rz={}
        for j in regions:
            dt=[]
            for k in dates:
                n={}
                if len(aws_na.objects.filter(date=str(k),service=str(i +' ('+j+')'))):
                    na=aws_na.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    n['date']=na.date
                    n['status']=na.status
                elif len(aws_sa.objects.filter(date=str(k),service=str(i +' ('+j+')'))):
                    sa=aws_sa.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    n['date']=sa.date
                    n['status']=sa.status
                elif len(aws_eu.objects.filter(date=str(k),service=str(i +' ('+j+')'))):
                    europe=aws_eu.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    n['date']=europe.date
                    n['status']=europe.status
                elif len(aws_ap.objects.filter(date=str(k),service=str(i +' ('+j+')'))):
                    ap=aws_ap.objects.get(date=str(k),service=str(i +' ('+j+')'))
                    n['date']=ap.date
                    n['status']=ap.status
                dt.append(n)
            rz[j]= dt
        d[i]= rz
    print dates
    return render(request, "cloup3.html", {'data':d,'date':dates})
"""

    def azure1(request):  
    dates=["Jul 18 2017","Jul 19 2017"]
    services = ['Redis Cache', 'Recommendations API']
    regions=['West US 2','West US','West India','UK West']
    data=[]
    s={}
    for i in services:
        for j in regions:
            
            for k in dates:
                    print k
                    if len(azure_asia.objects.filter(date=str(k),service=str(i +' ('+j+')'))):
                        asia=azure_asia.objects.get(date=str(k),service=str(i +' ('+j+')'))
                        if i in s:
                            if j in s[i]:
                                s[i][j].append(asia.status)
                            else:
                                s[i][j] =[k] 
                        else:
                            s[i] = { j : k}
                    if len(azure_americas.objects.filter(date=str(k),service=str(i +' ('+j+')'))):
                        america=azure_americas.objects.get(date=str(k),service=str(i +' ('+j+')'))
                        if i in s:
                            if j in s[i]:
                                s[i][j].append(america.status)
                            else:
                                s[i][j] =[k] 
                        else:
                            s[i] = { j : [k]}
                    if len(azure_europe.objects.filter(date=str(k),service=str(i +' ('+j+')'))):
                        europe=azure_europe.objects.get(date=str(k),service=str(i +' ('+j+')'))
                        if i in s:
                            if j in s[i]:
                                s[i][j].append(europe.status)
                            else:
                                s[i][j] =[k] 
                        else:
                            s[i] = { j : [k]}
    return render(request, "azure.html", {'data':s})
"""
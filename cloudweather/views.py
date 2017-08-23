from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from cloudweather.forms import SignUpForm
from necloudweather.models import *
from necloudweather.views import *
from django.template.loader import render_to_string
import ast,json
import boto3, datetime,decimal,math
from django.core.cache import cache
cache_time = 1800
access_key, secreat_key = 'AKIAI4ERU5DE52JGXOOQ', 'ttX+4uw0OtPKBKfxCOFIhPwKpFuoiFeUKFCJuh2u'
region_known_names = { 'us-east-2':'Ohio', 'us-east-1':'N. Virginia', 'us-west-1':'N. California', 'us-west-2':'Oregon',
                           'ca-central-1': 'Central', 'ap-south-1': 'Mumbai', 'ap-southeast-1':'Singapore', 'ap-southeast-2':'Sydney',
                           'ap-northeast-1':'Tokyo', 'ap-northeast-2':'Seoul', 'eu-central-1':'Frankfurt', 'eu-west-1':'Ireland',
                           'eu-west-2':'London', 'sa-east-1':'Sao Paulo' }
    
instance_family_type = {'r4.xlarge': '4', 'd2.2xlarge': '8', 'g2.8xlarge': '32', 'm3.2xlarge': '8', 't2.small': '1', 'c3.xlarge': '4',
                            'm4.2xlarge': '8', 'r3.4xlarge': '16', 'r4.16xlarge': '64', 'm1.small': '1', 'c1.medium': '2', 'm3.large': '2',
                            'f1.16xlarge': '64', 'r4.large': '2', 'i3.2xlarge': '8', 'i3.xlarge': '4', 't1.micro': '1', 'cr1.8xlarge': '32',
                            'r3.2xlarge': '8', 'c4.8xlarge': '36', 'm4.10xlarge': '40', 'r4.4xlarge': '16', 'm4.16xlarge': '64',
                            'p2.8xlarge': '32', 'c4.xlarge': '4', 'm1.large': '2', 'hs1.8xlarge': '17', 'c3.2xlarge': '8', 'g2.2xlarge': '8',
                            't2.2xlarge': '8', 'c3.4xlarge': '16', 'm4.large': '2', 't2.medium': '2', 't2.nano': '1', 'f1.2xlarge': '8',
                            'g3.8xlarge': '32', 'i2.8xlarge': '32', 'm2.2xlarge': '4', 'd2.4xlarge': '16', 't2.xlarge': '4', 'd2.8xlarge': '36',
                            'c4.4xlarge': '16', 'r4.2xlarge': '8', 'g3.4xlarge': '16', 't2.micro': '1', 'c1.xlarge': '8', 'r3.8xlarge': '32',
                            'm4.xlarge': '4', 'x1.32xlarge': '128', 'x1.16xlarge': '64', 'c4.2xlarge': '8', 'm2.xlarge': '2', 'p2.16xlarge': '64',
                            'p2.xlarge': '4', 'c3.8xlarge': '32', 'cc1.4xlarge': '16', 'm1.medium': '1', 'd2.xlarge': '4', 'r3.large': '2',
                            'i2.xlarge': '4', 'm3.medium': '1', 't2.large': '2', 'i2.4xlarge': '16', 'r3.xlarge': '4', 'c4.large': '2',
                            'cg1.4xlarge': '16', 'r4.8xlarge': '32', 'i2.2xlarge': '8', 'hi1.4xlarge': '16', 'c3.large': '2', 'cc2.8xlarge': '32',
                            'g3.16xlarge': '64', 'i3.16xlarge': '64', 'i3.large': '2', 'm1.xlarge': '4', 'i3.4xlarge': '16', 'm4.4xlarge': '16',
                            'm2.4xlarge': '8', 'i3.8xlarge': '32', 'm3.xlarge': '4'}
    
days_count = 7
period_seconds = 86400
idle_range = 20
    
    #Get ec2 regions
s = boto3.Session(aws_access_key_id = access_key, aws_secret_access_key = secreat_key)
ec2_regions =  s.get_available_regions('ec2')
def home_page(request):
    return HttpResponseRedirect('/necloudweather')

def user_login(request):
    context = {}
    if request.user.is_authenticated():
        return HttpResponseRedirect('/necloudweather')
    if request.method == 'GET':
        form = AuthenticationForm()
    elif request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request,form.user_cache)
            if request.user.is_authenticated():
                return HttpResponseRedirect('/necloudweather')
    context['form'] = form
    return render(request,'login.html',context)

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/necloudweather')
def registration(request):
    return render(request, "signup.html")
def user_profile(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    userdata = SavedFilter.objects.filter(user=request.user)
    return render(request,"profile.html", {"userdata":userdata})
def tempload(request):
    tempname = request.POST.get('env')
    if str(tempname).endswith(" "):
        tempname=str(tempname[:-1])
    else:
        tempname=str(tempname)
    tempname =str(tempname)
    print tempname
    userdata = SavedFilter.objects.filter(user=request.user,templatename=str(tempname))
    for i in userdata:
        if (str(i.cloudprovider)=="AWS"):
            all_region=aws_regions()
            all_service=aws_services()  
        elif (str(i.cloudprovider)=="Azure"):
            print "hi"
            all_region=azure_dc()
            all_service=azure_services()   
        elif (str(i.cloudprovider)=="Google"):
            all_region=google_regions()
            all_service=google_services()
        list1=[]
        list2=[]
        for j in [x.encode('UTF8') for x in ast.literal_eval(str(i.regions))]:
            for k in all_region:
                if str(j)==str(k):
                    list2.append(j)
                else:
                    list1.append(k)
        list3=[]
        list4=[]
        print list(set(list1) - set(list2))
        for j in [x.encode('UTF8') for x in ast.literal_eval(str(i.services))]:
            for k in all_service:
                if str(j)==str(k):
                    print k
                    list4.append(j)
                else:
                    list3.append(k)
        print list3    
    data=json.dumps({'all_region':list(set(list1) - set(list2)),'all_service':list(set(list3)-set(list4)),'regions': list(set(list2)),'services':  list(set(list4)),'cloud':str(i.cloudprovider),'fromdate':str(i.date1),'todate':str(i.date2) })
   
    return HttpResponse(json.dumps(data), content_type="application/json")
def tempdelete(request):
    tempname = request.POST.get('env')
    deleteobj = SavedFilter.objects.filter(user=request.user,templatename=str(tempname))
    deleteobj.delete()
    userdata = SavedFilter.objects.filter(user=request.user)
    templist=[]
    for i in userdata:
        templist.append(str(i.templatename))
    data=json.dumps({'templist':templist})
    return HttpResponse(json.dumps(data), content_type="application/json")    
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
def tempcheck(request):
    tempname = request.POST.get('env')
    userdata = SavedFilter.objects.filter(user=request.user,templatename=str(tempname))
    if(len(userdata)>0):
        status = 'ok'
    else:
        status = 'no'
    return HttpResponse(json.dumps(status), content_type="application/json")

def cpu(request):
    cache_key = "CPU"
    cpu=cache.get(cache_key)
    if not cpu:
        dict2={}
        for region in ec2_regions:
            ec2_client = boto3.client('ec2', region, aws_access_key_id = access_key, aws_secret_access_key = secreat_key)
            instances = ec2_client.describe_instances()
            list1=[]
            print region
            for instance in instances['Reservations']:
                dict1={}
                for i in instance['Instances']:
                    instanceid = i['InstanceId']
                    instancestate = i['State']['Name']
        
                    if instancestate == 'running':
                        instanceid = i['InstanceId']
                        instancetype = i['InstanceType']
                        my_dict = {}
        
                        cloudwatch_client = boto3.client('cloudwatch', region, aws_access_key_id=access_key, aws_secret_access_key=secreat_key)
                        data = cloudwatch_client.get_metric_statistics(Namespace='AWS/EC2', Unit='Percent',
                                                        Dimensions=[{'Name': 'InstanceId', 'Value': instanceid}],
                                                        MetricName='CPUUtilization',
                                                        StartTime=datetime.datetime.now() - datetime.timedelta(days=days_count),
                                                        EndTime=datetime.datetime.now(), Period=period_seconds, Statistics=['Average'])
        
        
                        for d in range(len(data['Datapoints'])):
                            my_dict.update({data['Datapoints'][d]['Timestamp']: data['Datapoints'][d]['Average']})
        
                        sum = 0
                        count = 0
                        d = sorted(my_dict.keys())
        
                        for c in d:
                            sum += my_dict[c]
                            count += 1
        
                        try:
                            average = (sum / count)
                        except:
                            average = 0
                        
                        no_of_core = int(instance_family_type[instancetype])
                        if average >= idle_range:
                            average_decimal = average/100
                            a = no_of_core * average_decimal
                            b = no_of_core * 0.20
                            t = a + b
                            dict1['ID']=instanceid
                            dict1['CPU']=round(average,2)
                            dict1['Core']=no_of_core
                            dict1['instancetype']=instancetype
                            dict1['Suggestion']=str(math.ceil(t))+' Core is Enough!!'
                        else:
                            dict1['ID']=instanceid
                            dict1['CPU']=round(average,2)
                            dict1['Core']=no_of_core
                            dict1['instancetype']=instancetype
                            dict1['Suggestion']='Idle State'
                list1.append(dict1)          
            dict2[region_known_names[region]]=list1
        cpu=dict2
        cache.set(cache_key,cpu,cache_time)
    return render(request, 'RI.html', {'data': cpu,'regions':aws_regions(),'services':aws_services()})
def RI(request):
    cache_key = "RIisisddsdd"
    ri=cache.get(cache_key)
    if not ri:
        rg={}
        for region in ec2_regions:
            client = boto3.client('ec2', region, aws_access_key_id = access_key, aws_secret_access_key = secreat_key)
            ri_response = client.describe_reserved_instances()
            #print region_known_names[region]
            no_of_ris_in_region = len(ri_response['ReservedInstances'])
            rs={}
            suggestion=''
            for reservedinstance in ri_response['ReservedInstances']:
                reservedinstanceid = reservedinstance['ReservedInstancesId']
                reservedinstancetype = reservedinstance['InstanceType']
                # reservedinstancetype = "X6-large"
        
                reservedinstanceend = reservedinstance['End']
                reservedinstancestate = reservedinstance['State']
                reservedinstancecount = reservedinstance['InstanceCount']
                reservedinstancecount = 5
        
                instances = client.describe_instances()
                count = 0
                res_instances = [ ]
                for instance in instances['Reservations']:
                    dict1={}
                    for i in instance['Instances']:
                        # print i
                        instancetype = i['InstanceType']
                        instancestate = i['State']['Name']
        
                        if instancetype == reservedinstancetype and instancestate == "running":
                            instanceid = i['InstanceId']
                            instancetag = i['Tags'][0]['Value']
                            count += 1
                            res_instances.append(instanceid)
                            # print count, instanceid
                            # print instanceid, instancetag
              
                #print "You used %s instances and they are %s under %s region. \n" % (count, res_instances, region_known_names[region])
        
                if reservedinstancecount <= count:
                    print " "
                    #print "You bought %s ri instances and it's type is %s under %s region, and you used all. \n" % (reservedinstancecount, reservedinstancetype, region_known_names[region])
                else:
		    suggestion += str(reservedinstancecount)+" RIs are Purchased in "+str(region_known_names[region]) +' for '+ str(reservedinstancetype)+'. \n You should move '+str(count)+' '+ str(reservedinstancetype) +' work load from On-demanding to RI instaces in  '+str(region_known_names[region])+'\n'
			#print "You bought %s ri instances and it's type is %s under %s region, but you used only %s. \n" % (reservedinstancecount, reservedinstancetype, region_known_names[region], count)
        
                    for sug_region in ec2_regions:
                        # if sug_region == region:
                        #     print "Same region"
                        if sug_region != region:
                            sug_client = boto3.client('ec2', sug_region, aws_access_key_id = access_key, aws_secret_access_key = secreat_key)
                            sug_instances = sug_client.describe_instances()
                            sug_count = 0
                            sug_region_count = 0
        
                            for sug_instance in sug_instances['Reservations']:
                                # no_sug = 0
                                # sug_region_count = 0
        
                                for s in sug_instance['Instances']:
                                    sug_instancestate = s['State']['Name']
                                    sug_instancetype = s['InstanceType']
                                    # print reservedinstancetype, sug_instancetype
        
        
                                    if reservedinstancetype == sug_instancetype and sug_instancestate == "running":
                                        #print "Suggestions %s region has same type of instance" % (sug_region)
                                        sug_region_count += 1
                                    # print sug_region_count, sug_region
                                    # else:
                                    #     if sug_count == 0:
                                    #         print "I didn't find any suggestions, because there is no %s running instances in all other regions" % (reservedinstancetype)
        
                            if sug_region_count > 0:
				suggestion += 'You shoud move '+str(sug_region_count)+' '+str(reservedinstancetype)+' work load from '+str(region_known_names[sug_region])+' to '+str(region_known_names[region])+'\n'
				#print "Under %s region you have %s suggested running instance" % (region_known_names[sug_region], sug_region_count)
                        else:
                            print "No suggestions"
                rs['ondemand-instances']=res_instances
                rs['suggestion']= suggestion
                rs['count']= reservedinstancecount
                rs['id']=reservedinstance['ReservedInstancesId']
                rs['type']=reservedinstance['InstanceType']
            rg[region_known_names[region]]=rs
        ri=rg
        cache.set(cache_key,ri,cache_time)
    return render(request, 'RI1.html', {'data': ri,'regions':aws_regions(),'services':aws_services()})



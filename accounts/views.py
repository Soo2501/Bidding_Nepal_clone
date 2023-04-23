from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from items.models import Item
from .models import Detail
from django.core.mail import send_mail
from datetime import date,timedelta
import datetime
# Create your views here.
def login(request):
    if request.method == 'POST':
        uname = request.POST.get('un','')
        pass1 = request.POST.get('pa','')
        user = auth.authenticate(username=uname,password=pass1)

        if user == None:
            messages.info(request,"invalid username/password")
            return redirect('login')
        else:
            auth.login(request,user)
            return redirect("home")
            
    else:
        return render(request,'login.html')


def register(request):
    if request.method == 'POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        name = request.POST['name']
        mail = request.POST['email']
        p1 = request.POST['p1']
        p2 = request.POST['p2']

        contact = request.POST['contact']
        if p1 == p2:
            if User.objects.filter(email=mail).exists():
                messages.info(request,"Already an User with this Email")
                return redirect('register')
            elif User.objects.filter(username=name).exists():
                messages.info(request,"Already an User with this Username")
                return redirect('register')
            else:
                user = User.objects.create_user(first_name=fname,last_name=lname,email=mail,password=p1,username=name)
                user.save()
                obj = Detail(username=name,contact=contact)
                obj.save()
                subject = "Online Bidding"  
                msg     = "Congratulations you are registered successfully."
                to      = mail  
                res     = send_mail(subject, msg, "bidding.nepal11@gmail.com", [to])
                if res == 1:
                    return redirect('/')
                else:
                    messages.info(request,"Some thing is wrong")
                    return redirect('register')
        else:
            messages.info(request,"Password does not match")
            return redirect('register')
    else:
        return render(request,'register.html')

def about(request):
    return render(request,'about.html')



@login_required(login_url='login')
def sendMailTowinners(request):
    today = date.today()
    yesterday = today - datetime.timedelta(days=1) 
    item = Item.objects.filter(start_date=yesterday).filter(sold="sold").filter(sendwinmail="unsended")
    for i in item :
        
        try:
            
            winnerid = i.highest_bidder
            user_obj = User.objects.get(id=winnerid)
            winnermail = user_obj.email


            winuser = user_obj.username
            #-----------------------------------------------------------
            obj = Detail.objects.get(username=winuser)
            wincon = obj.contact
            
            itemmail = i.ownermail
            itemUserobj = User.objects.get(email=itemmail)
            itemuser = itemUserobj.username

            obj2 = Detail.objects.get(username=itemuser)
            itemcon = obj2.contact

            subject = "Online Bidding"  
            msg     = "Congratulations you are winner of item"+i.name+"'s, Seller Email-id is "+i.ownermail+"  contact him for further informations. phone no = "+itemcon+" Thank You :)"
            to      = winnermail  
            res     = send_mail(subject, msg, "bidding.nepal11@gmail.com", [to])
            if res ==1:
                print ("mail sended to winner")
            else:
                print("something wrong for sending mail to winner")
            
            subject = "Online Bidding"  
            msg     = "Congratulations your item "+i.name+"'s higgest bidder's email id is "+winnermail+" ,  contact him for further informations. phone no = "+wincon +" Thank You :)"
            to      = i.ownermail  
            res     = send_mail(subject, msg, "bidding.nepal11@gmail.com", [to])
            if res ==1:
                print ("mail sended to seller")
            else:
                print("something wrong for sending mail to seller")
            i.sendwinmail="sended"
            i.save()
        except:
            pass



@login_required(login_url='login')
def pastConfigurations(request):
    item = Item.objects.all()
    for i in item:
        try:
            hb = i.highest_bidder
            if hb is not None:
                i.sold="sold"
                i.save()
            else:
                i.sold="unsold"
                i.save()
        except:
            pass

@login_required(login_url='login')
def home(request):
    items = Item.objects.all()
    today = date.today()
    yesterdays = today + datetime.timedelta(days=1) 

    for i in items:
        if(today > i.start_date):
            i.status = "past"
        if(today < i.start_date):
            i.status="future"
        if(today == i.start_date):
            i.status="live"
        i.save()
    pastConfigurations(request)
    sendMailTowinners(request)
    items = Item.objects.filter(status="live")
    items = Item.objects.filter(verified=True)
    Ending_date = yesterdays
    return render(request,"home.html",{'items':items, 'Ending_date': Ending_date})
    
def logout(request):
    auth.logout(request)
    return redirect("login") 

def ilogout(request):
    auth.logout(request)
    return redirect("login") 

@login_required(login_url='login')
def myprofile(request):
    bidder = request.user
    details = bidder   
    cuname = details.username
    obj = Detail.objects.filter(username=cuname)
    contact=""
    for i in obj:
        contact = i.contact
    return render(request,"myprofile.html",{"details":details,"contact":contact})

@login_required(login_url='login')
def log(request):
    cuser =request.user
    cmail = cuser.email
    cid = cuser.id
    item_obj = Item.objects.filter(highest_bidder=cid)

    biddeditem = item_obj
    pitem = Item.objects.filter(ownermail=cmail).filter(status="past") 
    litem = Item.objects.filter(ownermail=cmail).filter(status="live") 
    fitem = Item.objects.filter(ownermail=cmail).filter(status="future") 
    return render(request,"log.html",{'pitem':pitem,'litem':litem,'fitem':fitem,"biddeditem":biddeditem})

@login_required(login_url='login')
def future(request):
    items = Item.objects.filter(status="future")
    items = Item.objects.filter(verified=True)
    return render(request,"future.html",{"items":items})
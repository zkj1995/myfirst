import string
import random
import time
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import auth #登陆注册
from  django.contrib.auth.models import User
from django.core.mail import send_mail

from .forms import LoginForm,RegForm,ChangeNicknameForm,BindEmailForm,ChangePasswordForm,ForgotPasswordForm
from .models import Profile
# Create your views here.
def login(request):
    '''
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    referer = request.META.get('HTTP_REFERER',reverse('home')) #跳转原来页面否则跳转会主页
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return redirect(referer) #跳转
    else:
        return render(request,'error.html',{'message':'用户名或密码不正确'})
    '''
    if request.method == 'POST': #提交数据
        login_form = LoginForm(request.POST)
        if login_form.is_valid():  #是否有效
            user  = login_form.cleaned_data['user']
            auth.login(request,user)
            return redirect(request.GET.get('from',reverse('home')))

    else:                        #加载页面
        login_form = LoginForm()
    context={}
    context['login_form'] = login_form
    return render(request,'user/login.html',context)

def login_for_medal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():  # 是否有效
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] ='ERROR'
    return  JsonResponse(data)

def register(request):
    if request.method == 'POST': #提交数据
        reg_form = RegForm(request.POST,request=request)
        if reg_form.is_valid():  #是否有效

            username  = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            #方法1 创建用户
            user = User.objects.create_user(username,email,password)
            user.save()
            '''
            # 方法2
                user = User()
                user.username = username
                user.email =email
                user.set_password(password)
                user.save()
            '''
            # 清除session
            del request.session['register_code']
            #登陆用户
            user = auth.authenticate(username=username, password=password)  # 判断用户账号密码是否正确
            auth.login(request,user)
            return redirect(request.GET.get('from',reverse('home')))

    else:                        #加载页面
        reg_form = RegForm()
    context={}
    context['reg_form'] = reg_form
    return render(request,'user/register.html',context)


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))

def user_info(request):
    context = {}
    return render(request,'user/user_info.html',context)

def change_nickname(request):

    redirect_to = request.GET.get('from', reverse('home'))
    if request.method =='POST':
        form = ChangeNicknameForm(request.POST,user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nikename_new']
            profile,created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()
    context = {}
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['return_back_url'] = redirect_to
    context['form'] = form
    return render(request,'form.html',context)


def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method =='POST':
        form = BindEmailForm(request.POST,request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()
    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['return_back_url'] = redirect_to
    context['form'] = form
    return render(request,'user/bind_email.html',context)


def send_verification_code(request):
    email = request.GET.get('email','')
    send_for = request.GET.get('send_for','')
    data={}
    if email !='':
        # 生成验证码  随机生成包含数字和字母的四个字符串
        code =  ''.join(random.sample(string.ascii_letters + string.digits,4))  #加上string的字母和数字
        #生命周期两个星期

        now = int(time.time())
        send_code_time = request.session.get('send_code_time',0)

        if now-send_code_time <30:
            data['status'] = 'ERROR'
        else:
            # 发送邮件

            request.session[send_for] = code
            request.session['send_code_time'] = now
            # send_mail的参数分别是  邮件标题，邮件内容，发件箱(settings.py中设置过的那个)，收件箱列表(可以发送给多个人),失败静默(若发送失败，报错提示我们)
            send_mail(
                '我是邮件标题',
                '我们是:%s'% code,
                'test_email1@163.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def change_password(request):
    redirect_to =  reverse('home')
    if request.method =='POST':
        form = ChangePasswordForm(request.POST,user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            newa_password = form.cleaned_data['new_password']
            #user.set_password() 修改密码
            user.set_password(newa_password)
            user.save()
            #登陆操作
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()
    context = {}
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['return_back_url'] = redirect_to
    context['form'] = form
    return render(request,'form.html',context)


def forgot_password(request):
    redirect_to = reverse('login')
    if request.method =='POST':
        form = ForgotPasswordForm(request.POST,request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()
    context = {}
    context['page_title'] = '重置密码'
    context['form_title'] = '重载密码'
    context['submit_text'] = '重载'
    context['return_back_url'] = redirect_to
    context['form'] = form
    return render(request,'user/forgot_password.html',context)
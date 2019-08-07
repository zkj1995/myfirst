import datetime

from django.shortcuts import render,redirect
from  read_statistics.utils import  get_seven_days_read_data,get_today_hot_data,get_yesterday_hot_data
from django.contrib.contenttypes.models import ContentType
from blog.models import Blog
from django.db.models import  Sum
from django.utils import timezone #获取当前时间
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import auth #登陆注册
from  django.contrib.auth.models import User
from django.core.cache import cache


def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7) #前七天
    blogs = Blog.objects.filter(read_details__date__lt=today,read_details__date__gte=date)\
                        .values('id','title')\
                        .annotate(read_num_sum=Sum('read_details__read_num'))\
                        .order_by('-read_num_sum')
    return blogs




def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates,read_nums = get_seven_days_read_data(blog_content_type)
    today_hot_data = get_today_hot_data(blog_content_type)
    yesterday_hot_data = get_yesterday_hot_data(blog_content_type)

    #获取七天热门博客的缓存数据
    hot_data_for_7_blogs = cache.get('hot_data_for_7_blogs')
    if hot_data_for_7_blogs is None:
        hot_data_for_7_blogs = get_7_days_hot_blogs()
        cache.set('hot_data_for_7_blogs',hot_data_for_7_blogs,60*60) #保存一小时

    context ={}
    context['read_nums'] = read_nums
    context['dates'] = dates
    context['today_hot_data']= today_hot_data
    context['yesterday_hot_data'] = yesterday_hot_data
    context['hot_data_for_7_blogs'] = hot_data_for_7_blogs

    return  render(request,'home.html',context)


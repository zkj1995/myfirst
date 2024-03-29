import datetime
from django.db.models import Sum
from django.utils import timezone #获取当前时间
from django.contrib.contenttypes.models import ContentType

from  read_statistics.models import ReadNum,ReadDetail


def read_statistics_once_read(request,obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" %(ct.model,obj.pk)
    if  not request.COOKIES.get(key):
        '''
        if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():
            #存在记录
            readnum = ReadNum.objects.get(content_type=ct, object_id=obj.pk)

        else:
            #不存在对应记录
            readnum = ReadNum(content_type=ct, object_id=obj.pk)
        '''
        #总阅读数+1
        readnum, created =  ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1  #计数+1
        readnum.save()

        #当天阅读数+1
        date = timezone.now().date()
        '''
        if ReadDetail.objects.filter(content_type=ct, object_id=obj.pk,date=date).count():
            readDetail = ReadDetail.objects.get(content_type=ct, object_id=obj.pk,date=date)
        else:
            readDetail = ReadDetail(content_type=ct, object_id=obj.pk,date=date)
        '''
        readDetail,created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk,date=date)
        readDetail.read_num+=1
        readDetail.save()

    return  key

def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    dates= []
    read_nums= []
    for i in range(7,0,-1):
        date = today - datetime.timedelta(days=i)  #获取前6天
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type,date=date)
        result = read_details.aggregate(read_num_sum = Sum('read_num'))

        read_nums.append(result['read_num_sum'] or 0)
    return  dates,read_nums

def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type,date=today).order_by('-read_num') #指定对read_num由大到小排序
    return  read_details[:7]

def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type,date=yesterday).order_by('-read_num') #指定对read_num由大到小排序
    return read_details[:7]

def get_7_days_hot_data(content_type):
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7) #前七天
    read_details = ReadDetail.objects.filter(content_type=content_type, date__lt=today,date__gte=date)\
                                     .values('content_type','object_id')\
                                     .annotate(read_num_sum= Sum('read_num'))\
                                     .order_by('-read_num_sum')  # 指定对read_num由大到小排序
    return read_details[:7]


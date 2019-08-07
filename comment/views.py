from django.shortcuts import render,redirect
from .models import Comment
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
# Create your views here.
from .forms import CommentForm
from django.http import JsonResponse

def update_comment(request):
    ''''
    user = request.user
    referer = request.META.get('HTTP_REFERER', reverse('home'))  # 跳转原来页面否则跳转会主页
    #数据检查
    if user.is_authenticated:
        render(request, 'error.html', {'message': '用户未登录','redirect_to':referer})
    text = request.POST.get('text','').strip()
    if text=='':
        return render(request,'error.html',{'message':'评论内容不能为空','redirect_to':referer})

    try:
        content_type = request.POST.get('content_type','')
        object_id = int(request.POST.get('object_id',''))
        model_class = ContentType.objects.get(model=content_type).model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except Exception as e:
        return render(request,'error.html',{'message':'评论对象不存在','redirect_to':referer})

    comment= Comment()
    comment.user = user
    comment.text = text
    #Blog.objects.get(pk=object_id)
    comment.content_object = model_obj
    comment.save()

    return redirect(referer)
    '''
    referer = request.META.get('HTTP_REFERER', reverse('home'))  # 跳转原来页面否则跳转会主页
    # 数据检查 去掉了 后端写了
    comment_form = CommentForm(request.POST,user=request.user)
    data = {}
    if comment_form.is_valid():
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        # Blog.objects.get(pk=object_id)
        comment.content_object = comment_form.cleaned_data['content_object']

        parent = comment_form.cleaned_data['parent']
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user

        comment.save()

        #发送邮件通知
        comment.send_email()

        #返回数据
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.get_nickname_or_username()
        #
        data['comment_time'] =comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
        data['text'] = comment.text
        data['content_type'] = ContentType.objects.get_for_model(comment).model

        if not parent is None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ''  #空

        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''
        #return redirect(referer)
    else:
        #return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})
        data['message'] = list(comment_form.errors.values())[0][0]
        data['status'] = 'ERROR'
    return JsonResponse(data)


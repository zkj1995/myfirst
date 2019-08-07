from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from ckeditor.widgets import CKEditorWidget
from .models import Comment

class CommentForm(forms.Form):
    content_type  = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor'),
                           error_messages={'required':'评论内容不能为空'})

    reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id':'reply_comment_id'}))

    def __init__(self,*args,**kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(CommentForm, self).__init__(*args,**kwargs)  #调用基类的__init__()构造函数 py2写法
        #super().__init__(*args,**kwargs) #py3 写法
    def clean(self):
        #判断用户是否登陆
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')

        #评论对象验证
        content_type= self.cleaned_data['content_type']
        object_id = self.cleaned_data['object_id']
        try:
            model_class = ContentType.objects.get(model=content_type).model_class()
            model_obj = model_class.objects.get(pk=object_id)
            self.cleaned_data['content_object'] = model_obj
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论对象不存在')
        return  self.cleaned_data


    def clean_reply_comment_id(self):
        reply_comment_id =self.cleaned_data['reply_comment_id']
        if reply_comment_id<0:
            raise forms.ValidationError('回复出错')
        elif reply_comment_id ==0:
            self.cleaned_data['parent'] = None
        elif Comment.objects.filter(pk=reply_comment_id).exists():
            self.cleaned_data['parent'] = Comment.objects.get(pk=reply_comment_id)#这个必须是get操作
        else:
            raise forms.ValidationError('回复出错')
        return  reply_comment_id
    """
    django的get是从数据库的取得一个匹配的结果，返回一个对象，如果记录不存在的话，它会报错。 
    用django的get去取得关联表的数据的话，而关键表的数据如果多于2条的话也会报错。 
     
    django的filter方法是从数据库的取得匹配的结果，返回一个对象列表，如果记录不存在的话，它会返回[]。     
    """


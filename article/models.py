from django.db import models
from django.utils import timezone
from  django.contrib.auth.models import User
# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    #三种方式设置时间
    #created_time = models.DateTimeField()
    #created_time = models.DateTimeField(default=timezone.now())
    created_time = models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User,on_delete=models.CASCADE,default=1)

    is_deleted = models.BooleanField(default=False)
    readed_num = models.IntegerField(default=0)



    def __str__(self):
        return "<Article:%s>"%self.title

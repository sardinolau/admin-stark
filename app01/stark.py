

from stark.service.stark import site,ModelStark
from .models import UserInfo,Book
from django.forms import ModelForm


class UserConfig(ModelStark):
    list_display = ['nid','name','age']
    # list_display_links = ['name']
    search_fields = ['name','age']
    actions = []
    list_filter = ['name','age']

class BookFormDemo(ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

class BookConfig(ModelStark):
    list_display = ['title','publish','price']
    model_form = BookFormDemo
    list_filter = ['publish','price']

#注册表和表的配置
site.register(UserInfo,UserConfig)
site.register(Book,BookConfig)

# print('register',site._registry)
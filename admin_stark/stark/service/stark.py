from django.urls import path,re_path
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from stark.utils.page import Pagination
from django.db.models import Q
#展示显示页面用
class ShowList(object):
    def __init__(self,config,data_list,request,):
        self.config = config
        self.data_list = data_list
        self.request = request
        #分页
        data_count = self.data_list.count()
        base_path = self.request.path
        current_page = int(self.request.GET.get("page", 1))
        self.pagination = Pagination(current_page,data_count,base_path,self.request.GET,per_page_num=5, pager_count=11,)
        self.page_data = self.data_list[self.pagination.start:self.pagination.end]
        #取actions
        self.actions = self.config.new_actions_list()

    def get_filter_linktag(self):
        import copy

        print('list_filter',self.config.list_filter)
        link_dict = {}
        for filter_field in self.config.list_filter:
            cid = self.request.GET.get(filter_field,0)
            # print("cid",cid)
            params = copy.deepcopy(self.request.GET)
            # print("filter_filter:",filter_field)
            filter_obj = self.config.model._meta.get_field(filter_field)
            print('filter_obj',filter_obj)
            from django.db.models.fields.related import ForeignKey,ManyToManyField
            if isinstance(filter_obj,ForeignKey) or isinstance(filter_obj,ManyToManyField):
                data_list = filter_obj.remote_field.model.objects.all()  #取到关联表中的所有字段
            else:
                data_list = self.config.model.objects.all().values('pk',filter_field)
            print(type(filter_obj))
            tmp = []

            #处理全部标签
            if params.get(filter_field):
                del params[filter_field]
                tmp.append('<a href="?%s">全部</a>'%params.urlencode())
            else:
                tmp.append('<a class="active" href="#">全部</a>')
                #处理数据标签
            for obj in data_list:
                print("obj",obj)
                if isinstance(filter_obj, ForeignKey) or isinstance(filter_obj, ManyToManyField):
                    pk = obj.pk
                    text = str(obj)
                    params[filter_field] = pk
                else:
                    pk = obj.get('pk')
                    text = obj.get(filter_field)
                    print("text",text)
                    params[filter_field] = text

                _url = params.urlencode()
                if int(cid) == text:
                    link_tag = '<a class="active" href="?%s">%s</a>'%(_url,text)
                else:
                    link_tag = '<a href="?%s">%s</a>' % (_url, text)
                tmp.append(link_tag)
            link_dict[filter_field]=tmp
            print(link_dict)
        return link_dict

    def get_action_list(self):
        tmp = []
        for action in self.actions:
            tmp.append({
                "name":action.__name__,
                "desc":action.short_description
            })
        return tmp

    def get_header(self):
        # 创建表头
        header_list = []
        for field in self.config.new_list_display():
            if callable(field):
                val = field(self.config, header=True)
                header_list.append(val)
            else:
                if field == '__str__':
                    header_list.append(self.config.model._meta.model_name.upper())
                else:
                    # header_list.append(field)
                    val = self.config.model._meta.get_field(field).verbose_name
                    header_list.append(val)
        return header_list
    def get_body(self):
        # 构建表单
        new_data_list = []
        for obj in self.page_data:
            tmp = []
            for field in self.config.new_list_display():  # ["name","age",edit]
                if callable(field):
                    val = field(self.config, obj)
                else:
                    val = getattr(obj, field)
                    if field in self.config.list_display_links:
                        _url = self.config._url(obj)
                        val = mark_safe('<a href="%s">%s</a>' % (_url, val))
                tmp.append(val)
            new_data_list.append(tmp)
        return new_data_list

class ModelStark(object):
    list_display = ["__str__"]
    list_display_links = []
    model_form = []
    search_fields = []
    actions = []
    list_filter = []

    def patch_delete(self,request,queryset):
        print('queryset:',queryset)
        queryset.delete()
    patch_delete.short_description = "批量删除"


    def new_actions_list(self):
        tmp = []
        tmp.append(ModelStark.patch_delete)
        tmp.extend(self.actions)

        return tmp

    def __init__(self,model,site):
        self.model = model
        self.site = site

    def _url(self,obj=None):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_change" % (app_label, model_name), args=(obj.pk,))
        return _url

    def get_model_form(self):
        if not self.model_form:
            from django.forms import ModelForm
            from django.forms import widgets as wid
            class ModelFormDemo(ModelForm):
                class Meta:
                    model = self.model
                    fields = '__all__'
                    # widgets = {
                    #     "name": wid.TextInput(attrs={"class": "form-control"})
                    # }
            return ModelFormDemo
        else:
            return self.model_form

    #删除，编辑，复选框
    def edit(self,obj=None,header=False):
        if header:
            return "编辑"
        # return mark_safe("<a herf='%s/change'>编辑</a>"%obj.pk)
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_change"%(app_label,model_name),args=(obj.pk,))
        return mark_safe("<a href='%s/change'>编辑</a>"%_url)

    def deletes(self,obj=None,header=False):
        if header:
            return "删除"
        # return mark_safe("<a herf='%s/change'>编辑</a>"%obj.pk)
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_delete"%(app_label,model_name),args=(obj.pk,))
        return mark_safe("<a href='%s/delete'>删除</a>"%_url)

    def checkbox(self,obj=None,header=False):
        if header:
            return mark_safe('<input id="choice" type="checkbox">')
        return mark_safe('<input class="choice_item"   type="checkbox" name="selected_pk" value="%s">'%obj.pk)

    def add_view(self, request):

        ModelFormDemo=self.get_model_form()
        form = ModelFormDemo()
        #实现+号窗口添加一对多，多对多数据
        for bfield in form:
            # print("bfield:",type(bfield))
            from django.forms.boundfield import BoundField
            from django.forms.models import ModelChoiceField
            field = bfield.field
            if isinstance(field,ModelChoiceField):
                bfield.is_pop=True
            related_model_name=bfield.field
            print(related_model_name)

        if request.method == "POST":
            form = ModelFormDemo(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request, 'add_view.html', locals())




        return render(request,'add_view.html',locals())

    def delete_view(self, request, id):
        url = self.get_list_url()
        if request.method == "POST":
            delete_obj = self.model.objects.filter(pk=id).delete()
            return redirect(url)
        return render(request,'delete_view.html',locals())

    def change_view(self, request, id):
        ModelFormDemo = self.get_model_form()
        change_obj = self.model.objects.filter(pk=id).first()
        if request.method == "POST":
            form = ModelFormDemo(request.POST,instance=change_obj)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())

        form = ModelFormDemo(instance=change_obj)

        return render(request,'change_view.html',locals())

#获取增删改查页面连接
    def get_add_url(self):
        return "add"
    def get_delete_url(self):
        return "delete"
    def get_change_url(self):
        return "change"
    def get_list_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_list_view" % (app_label, model_name))
        return _url



    def new_list_display(self):
        tmp = []
        tmp.append(ModelStark.checkbox)
        tmp.extend(self.list_display)
        if not self.list_display_links:
            tmp.append(ModelStark.edit)
        tmp.append(ModelStark.deletes)

        return tmp


    def search_condition(self,request):
        # 查询过滤
        key_word = request.GET.get("q","")
        self.key_word = key_word

        search_connection = Q()
        if key_word:
            search_connection = Q()
            search_connection.connector = "or"
            for search_field in self.search_fields:
                search_connection.children.append((search_field + "__contains", key_word))
                print(search_connection)
        return search_connection

    def get_filter_condition(self,request):
        # 获取filter的Q对象
        filter_condition = Q()
        for filter_field, val in request.GET.items():
            if filter_field in self.list_filter:
                filter_condition.children.append((filter_field,val))
        return filter_condition



    def list_view(self, request):
        if request.method=="POST":
            print("post:",request.POST)
            action = request.POST.get('action') #patch_init
            selected_pk = request.POST.getlist('selected_pk')
            action_func = getattr(self,action)
            queryset = self.model.objects.filter(pk__in = selected_pk)
            action_func(request,queryset)
        #获取筛选Q值
        search_connection = self.search_condition(request)
        # 获取筛选条件
        filter_condition = self.get_filter_condition(request)

        #获取筛选对象
        data_list = self.model.objects.all().filter(search_connection).filter(filter_condition)
            #获取表中所有数据
            # data_list = self.model.objects.all()

        #获取展示页面数据
        showlist = ShowList(self,data_list,request)


        print(self.list_display)

        #构造查看URL
        add_url = self.get_add_url()
        return render(request,'list_view.html',locals())

    def get_url2(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        tmp = []
        tmp.append(re_path('add/', self.add_view,name="%s_%s_add"%(app_label,model_name)))
        tmp.append(re_path('(\d+)/delete/', self.delete_view,name="%s_%s_delete"%(app_label,model_name)))
        tmp.append(re_path('(\d+)/change/', self.change_view,name="%s_%s_change"%(app_label,model_name)))
        tmp.append(re_path(r"^$", self.list_view,name="%s_%s_list_view"%(app_label,model_name)))
        return tmp

    @property
    def url2(self):
        return self.get_url2(), None, None



class StarkSite(object):
    def __init__(self):
        self._registry = {}
    def register(self,model,stark_class=None):
        if not stark_class:
            stark_class = ModelStark
        self._registry[model] = stark_class(model,self)




    def get_urls(self):
        tmp = []
        for model,stark_class_obj in self._registry.items():
            model_name = model._meta.model_name
            app_label = model._meta.app_label
            #分发增删改查
            tmp.append(re_path('%s/%s/'%(app_label,model_name),stark_class_obj.url2))

        return tmp


    @property
    def urls(self):

        return self.get_urls(),None,None

site = StarkSite()
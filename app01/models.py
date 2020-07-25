from django.db import models

# Create your models here.
class UserInfo(models.Model):
    nid = models.AutoField(primary_key = True)
    name = models.CharField(verbose_name="名字", max_length=32)
    age = models.IntegerField(verbose_name="年龄")

    def __str__(self):
        return self.name

class Book(models.Model):
    nid = models.AutoField(primary_key = True)
    title = models.CharField(verbose_name="书名",max_length=32)
    publish = models.ForeignKey(to='Publish',to_field='nid',verbose_name="出版社",max_length=32,on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name="价格",max_digits=6,decimal_places=0)
    author = models.ManyToManyField(to='Author',verbose_name='作者')
    def __str__(self):
        return self.title

class Publish(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name="出版社",max_length=32)
    def __str__(self):
        return self.title

class Author(models.Model):
    nid = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="作者",max_length=32)

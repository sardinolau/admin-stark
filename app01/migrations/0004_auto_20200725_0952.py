# Generated by Django 3.0.6 on 2020-07-25 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0003_auto_20200630_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('nid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32, verbose_name='作者')),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='author',
            field=models.ManyToManyField(to='app01.Author', verbose_name='作者'),
        ),
    ]
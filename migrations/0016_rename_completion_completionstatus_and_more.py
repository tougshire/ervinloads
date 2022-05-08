# Generated by Django 4.0.4 on 2022-05-08 14:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ervinloads', '0015_rename_status_deliverystatus_alter_location_name'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Completion',
            new_name='CompletionStatus',
        ),
        migrations.RenameField(
            model_name='load',
            old_name='completion',
            new_name='completion_status',
        ),
        migrations.AlterField(
            model_name='deliverystatus',
            name='name',
            field=models.CharField(help_text='The delivery status of the load', max_length=50),
        ),
        migrations.AlterField(
            model_name='load',
            name='delivery_status',
            field=models.ForeignKey(help_text='The delivery status of the load', null=True, on_delete=django.db.models.deletion.SET_NULL, to='ervinloads.deliverystatus'),
        ),
    ]
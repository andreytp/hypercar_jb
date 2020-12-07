# from django.db.models import Model
# from django.db.models import CharField, IntegerField, ForeignKey, DateTimeField, CASCADE, AutoField, BooleanField
from django.db import models

# Create your models here.
from django.forms import ModelForm


class Auto_service(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    url = models.CharField(max_length=128)
    duration = models.IntegerField(default=0)
    workplaces = models.IntegerField(default=0)

    class Meta:
        ordering = ["duration"]



class Task(models.Model):
    id = models.AutoField(primary_key=True)
    car = models.CharField(max_length=256)
    service_id = models.ForeignKey(Auto_service, on_delete=models.CASCADE)
    queue_number = models.IntegerField(default=0)
    registration = models.DateTimeField()



class Clients_queue(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(Auto_service, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    at_work = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    is_next = models.BooleanField(default=False)
    done_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ["service__duration", "task__registration"]

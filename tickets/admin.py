from django.contrib import admin
from .models import Auto_service, Task, Clients_queue


class Auto_servicesAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'duration', 'workplaces']
    list_filter = ['name', 'url', 'duration', 'workplaces']


class TaskAdmin(admin.ModelAdmin):
    list_display = ['car', 'service_id', 'queue_number', 'registration']
    list_filter = ['car', 'service_id', 'queue_number', 'registration']


class Clients_queueAdmin(admin.ModelAdmin):
    list_display = ['task', 'service', 'done', 'done_date']
    list_filter = ['task', 'service', 'done', 'done_date']


admin.site.register(Auto_service, Auto_servicesAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Clients_queue, Clients_queueAdmin)

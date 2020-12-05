from datetime import datetime
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views import View
from .models import Auto_service, Task, Clients_queue


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


def get_services(href_prefix: str) -> str:
    res = '<nav>'
    for item in Auto_service.objects.order_by('duration'):
        res += f'   >>>>>  <a href="{href_prefix}/{item.url}">{item.name}</a>'
    res += '   >>>>>  <a href="processing">Processing</a>'
    res += '   >>>>>  <a href="erase_queue">Erase queue</a>'

    return res + '</nav>'


class MenuView(View):

    def get(self, request, *args, **kwargs) -> HttpResponse:
        return HttpResponse(get_services('/get_ticket'))




def get_ticket(request, **kwargs) -> HttpResponse:
    request_command = kwargs.get('problem')
    if not request_command:
        raise PermissionError

    q_num, time_in_line = register_new_task(request_command)
    return HttpResponse(f'<div>Your number is {q_num}</div>'
                        f'<div>Please wait around {time_in_line} minutes</div>')

def find_service_by_url(url: str) -> Auto_service:
    return Auto_service.objects.get(url=url)

def register_new_task(request_command):
    required_service = find_service_by_url(request_command)
    if not required_service:
        raise PermissionError
    q_set = Clients_queue.objects.filter(done=False)
    q_num = len(q_set)
    s_set = Auto_service.objects.all()
    time_in_line = 0
    for indx, srv in enumerate(s_set):
        q_len = len(q_set.filter(service=srv))

        time_in_line += q_len * srv.duration
        if srv == required_service:
            break
    task_item = Task(service_id=required_service,
                car='AA0001AA',
                registration=datetime.now(),
                queue_number=q_num
                )
    task_item.save()
    Clients_queue.objects.create(service=required_service,
                                 task=task_item,
                                 done=False,
                                 )
    return q_num + 1, time_in_line

def erase_queue(request)->HttpResponse:
    Clients_queue.objects.all().delete()
    Task.objects.all().delete()
    return redirect('/menu')

def processing(request)->HttpResponse:
    http_response = ""
    q_set = Clients_queue.objects.filter(done=False)
    s_set = Auto_service.objects.all()
    for srv in s_set:
        q_len = len(q_set.filter(service=srv))
        http_response += f'<div>{srv.name} queue: {q_len}</div>'
    http_response += '''
    <form method="post">{% csrf_token %}
        <button type="submit">Process next</button>
    </form>
    '''
    return HttpResponse(http_response)

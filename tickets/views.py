from datetime import datetime
from django.http.response import HttpResponse
from django.template import RequestContext
from django.template import Template
from django.shortcuts import redirect, render
from django.views import View
from django.db.models import Sum
from .models import Auto_service, Task, Clients_queue


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


def get_services(href_prefix: str) -> str:
    res = '<nav>'
    for item in Auto_service.objects.order_by('duration'):
        res += f'   >>>>>  <a href="{href_prefix}/{item.url}">{item.name}</a>'
    res += '   >>>>>  <a href="processing">Processing</a>'
    res += '   >>>>>  <a href="next">Next</a>'
    res += '   >>>>>  <a href="erase_queue">Erase queue</a>'
    res += '</nav>'
    res += '<br/>'
    res += '<br/>'
    res += render_inline()
    res += '<br/>'
    res += '<br/>'
    res += render_queue()

    return res


def render_queue():
    queue = Clients_queue.objects.order_by('task__queue_number').all()
    str = ''
    for item in queue:
        str += f"<div>Client #{item.task.queue_number} on {item.service.name} {'done' if item.done else 'at work' if item.at_work else 'in queue'}</div>"
    return str


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


def get_workplaces_count() -> int:
    return Auto_service.objects.all().aggregate(Sum('workplaces'))['workplaces__sum']


def get_task_at_work_count(srv: Auto_service) -> int:
    return len(Clients_queue.objects.filter(at_work=True, service=srv))


def register_new_task(request_command):
    required_service = find_service_by_url(request_command)
    if not required_service:
        raise PermissionError
    undone_task = Clients_queue.objects.filter(done=False)
    task_at_work_count = get_task_at_work_count(required_service)
    undone_task_count = len(Clients_queue.objects.all())

    time_in_line = 0
    workplaces = get_workplaces_count()
    for index, service in enumerate(Auto_service.objects.all()):
        q_len = len(undone_task.filter(service=service, done=False, at_work=False))

        time_in_line += q_len * service.duration
        if service == required_service:
            break
    task_item = Task(service_id=required_service,
                     car='AA0001AA',
                     registration=datetime.now(),
                     queue_number=undone_task_count + 1
                     )
    task_item.save()
    Clients_queue.objects.create(service=required_service,
                                 task=task_item,
                                 at_work=(task_at_work_count < workplaces),
                                 done=False,
                                 )
    return undone_task_count + 1, time_in_line


def erase_queue(request) -> HttpResponse:
    Clients_queue.objects.all().delete()
    Task.objects.all().delete()
    return redirect('/menu')


def process_POST(request) -> HttpResponse:
    task_for_done = Clients_queue.objects.filter(at_work=True)
    if len(task_for_done) > 0:
        task = task_for_done.first()
        task.done = True
        task.at_work = False
        task.is_next = False
        task.done_date = datetime.now()
        task.save()

    task_for_work = Clients_queue.objects.filter(done=False)
    if len(task_for_work) > 0:
        task = task_for_work.first()
        task.done = False
        task.at_work = True
        task.is_next = True
        task.save()
    return redirect('/processing')


def processing(request) -> HttpResponse:
    if request.POST:
        return process_POST(request)

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
    template = Template(http_response)
    rendered_template = template.render(RequestContext(request))
    return HttpResponse(rendered_template)


def next_in_line(request) -> HttpResponse:
    rendered = render_inline()
    return HttpResponse(rendered)


def render_inline():
    rendered = '<div>Waiting for the next client</div>'
    next_task = Clients_queue.objects.filter(is_next=True)
    if len(next_task) > 0:
        num = next_task.first().task.queue_number
        rendered = f'<div>Next ticket #{num}</div>'
    return rendered

from collections import deque
from typing import Dict, List, Any, Union


class Service:
    local_queue = None
    last_task = None
    duration = 0
    url = ''
    name = ''

    def __init__( self, name, **kwargs ):
        self.name = name
        self.local_queue = deque('')
        for key, value in kwargs.items():
            if key == "duration":
                self.duration = value
                continue
            if key == 'url':
                self.url = value

    def queue_add( self, task ):
        self.local_queue.append(task)

    def queue_remove( self ):
        self.last_task = self.local_queue.popleft()

    def get_task_position( self, task ):
        try:
            pos = self.local_queue.index(task)
        except ValueError:
            return len(self.local_queue)
        return pos

    def get_duration_time( self, task ):
        return self.duration * self.get_task_position(task)

    @property
    def get_queue_len( self ) -> int:
        return len(self.local_queue)


class Task:

    def __init__( self, car: str, service: Service ):
        self.queue_number = 0
        self.car = car
        self.service = service
        # self.service.queue_add(self)


class Services_Queue:

    def __init__( self ):
        self.service_list = []
        self.last_on_line = None

    @property
    def get_last_queue_number( self ) -> int:
        queue_amount = 0
        for service in self.service_list:
            queue_amount += service.get_queue_len
        return queue_amount

    def get_service_by_url( self, url: str ) -> Service:
        return next(item for item in self.service_list if item.url == url)

    def get_duration_time( self, task: Task ) -> int:
        time = 0
        for service_item in self.service_list:
            time += service_item.get_duration_time(task)
            if service_item is task.service:
                break
        return time

    def add_service( self, service: Service ):
        self.service_list.append(service)
        self.service_list = sorted(self.service_list, key=lambda service_item: service_item.duration)

    def start_next_task( self ):
        for service_item in self.service_list:
            if service_item.get_queue_len != 0:
                service_item.queue_remove()
                break

    def get_service_by_name( self, name: str ) -> Service:
        return next(item for item in self.service_list if item.name == name)

    def add_task( self, task: Task ):
        task.service.queue_add(task)
        queue_number = 0
        if self.last_on_line:
            queue_number = self.last_on_line.queue_number + 1
        task.queue_number = queue_number
        self.last_on_line = task

    @property
    def get_whole_queue( self ):
        total_time = 0
        whole_queue: list[dict[str, int]] = []
        for service in self.service_list:
            for task in service.local_queue:
                whole_queue.append({'task': task,
                                    'estimate_time': total_time,
                                    })
                total_time += service.duration
        return whole_queue

    def whole_queue_print( self ):
        for index, task_item in enumerate(self.get_whole_queue):
            task = task_item.get("task")
            print(f'number:{task.queue_number}\t'
                  f'car:{task.car}\t'
                  f'service:{task.service.name}\t'
                  f'now_number:{index}\t'
                  f'estimate_time:{task_item.get("estimate_time")}')


def init_service_center():
    serv_queue = Services_Queue()
    service_to_add = Service("Change oil", url="change_oil", duration=2)
    serv_queue.add_service(service_to_add)
    service_to_add = Service("Inflate tires", url="inflate_tires", duration=5)
    serv_queue.add_service(service_to_add)
    serv_queue.add_service(Service("Diagnostic test", url="diagnostic", duration=30))

    return serv_queue


def gives_ticket_by_url( srv_queue: Services_Queue, url: str, auto: str ) -> dict:
    service = srv_queue.get_service_by_url(url)
    task = Task(auto, service)
    srv_queue.add_task(task)
    return {'queue_number': task.queue_number,
            'duration': srv_queue.get_duration_time(task)}


def main():
    q = init_service_center()
    print(gives_ticket_by_url(q, 'change_oil', 'BK3452CC'))
    print(gives_ticket_by_url(q, 'change_oil', 'AK3652CT'))

    print(gives_ticket_by_url(q, 'inflate_tires', 'AM9865HT'))
    print(gives_ticket_by_url(q, 'inflate_tires', 'AM0005KT'))
    print(gives_ticket_by_url(q, 'inflate_tires', 'AM0005KT'))

    print(gives_ticket_by_url(q, 'diagnostic', 'AA0101AI'))
    print(gives_ticket_by_url(q, 'diagnostic', 'AI3716BB'))

    q.whole_queue_print()
    q.start_next_task()
    print(gives_ticket_by_url(q, 'change_oil', 'AE3642CH'))
    q.start_next_task()
    print()
    print(gives_ticket_by_url(q, 'inflate_tires', 'AA7694TA'))
    q.start_next_task()
    print()
    print(gives_ticket_by_url(q, 'diagnostic', 'AO4527CM'))
    q.start_next_task()
    print()
    q.whole_queue_print()
    q.start_next_task()
    print()
    q.whole_queue_print()


if __name__ == "__main__":
    main()

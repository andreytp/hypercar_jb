from django.urls import path
from .views import WelcomeView, MenuView, get_ticket, erase_queue, processing, next_in_line

urlpatterns = [
    path('',  WelcomeView.as_view()),
    path('welcome/', WelcomeView.as_view()),
    path('menu', MenuView.as_view()),
    path('get_ticket/<str:problem>', get_ticket),
    path('erase_queue', erase_queue),
    path('processing', processing),
    path('next', next_in_line),
]

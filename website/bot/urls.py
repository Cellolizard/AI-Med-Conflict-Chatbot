from django.urls import path

from . import views

urlpatterns = [
    # ex: /bot/
    path('', views.index, name='index'),
    path('converse', views.conversation_view)
]

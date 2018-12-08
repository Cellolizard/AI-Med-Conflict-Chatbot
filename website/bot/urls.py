from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # ex: /bot/
    path('', views.index, name='index'),
    path('converse', views.conversation_view),
    path('converse_ajax', views.conversation_ajax)
]

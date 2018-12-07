from django.urls import path

from . import views

urlpatterns = [
    # ex: /bot/
    path('', views.index, name='index'),
    path('converse', views.conversation_view)
    # ex: /bot/5/
    # path('<int:question_id>/', views.detail, name='detail'),
    # ex: /bot/5/results/
    # path('<int:question_id>/results/', views.results, name='results'),
    # ex: /bot/5/vote/
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]

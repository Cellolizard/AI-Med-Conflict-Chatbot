from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Question

from .chatbot import *

def index(request):
    bot_response = converse('hello')
    context = {'bot_response': bot_response}
    return render(request, 'bot/index.html', context)

def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from .chatbot import *
from .models import Question
from .forms import ConversationForm

@csrf_exempt
def conversation_view(request):
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            bot_response = converse(form.cleaned_data['converse'])
            context = {'bot_response': bot_response}
            return render(request, 'bot/index.html', context)

@csrf_exempt
def index(request):
    print('Called the wrong thing')
    bot_response = converse('hello')
    context = {'bot_response': bot_response}
    return render(request, 'bot/index.html', context)

from django import forms

class ConversationForm(forms.Form):
    converse = forms.CharField(label='Talk to me!', max_length=250)

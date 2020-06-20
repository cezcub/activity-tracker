from django import forms

class TriviaForm(forms.Form):
	answer = forms.CharField(max_length=100)
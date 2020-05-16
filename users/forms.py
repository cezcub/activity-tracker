from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CreateParticipant(forms.Form):
	age_groups = [('below 5', 'below 5'), ('5-8','5-8'), ('9-10','9-10'), ('11-18','11-18'), ('18+','18+')]
	first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder':'Please enter the participants first name.', 'size': 33}))
	age_group = forms.ChoiceField(choices=age_groups)

class CreateActivity(forms.Form):
	activity_choices = [('Biking','Biking'), ('Walking', 'Walking'), ('Running','Running')]
	activity_type = forms.ChoiceField(choices=activity_choices)
	date = forms.DateField(widget=forms.DateInput(attrs={'placeholder':'Enter as month/day/year - 01/01/20', 'size': 33}))
	miles = forms.DecimalField(max_digits=2, decimal_places=1)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

from django import forms
from django.contrib.auth.models import User
from price.models import UserProfile

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	cardID = forms.CharField()
	
	class Meta:
		model = User
		fields = ('username', 'email', 'password', 'cardID')

class UserProfileForm(forms.ModelForm):

	class Meta:
		model = UserProfile
		fields = ('cardID',)
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from users.mixins.forms import FormAttrMixin

class LoginForm(AuthenticationForm):
	username = forms.CharField(
		label='Username',
		max_length=254,
		widget=forms.TextInput(attrs=FormAttrMixin.username_attrs)
	)
	password = forms.CharField(
		label='Password',
		widget=forms.PasswordInput(attrs=FormAttrMixin.password_attrs)
	)

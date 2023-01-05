from django.contrib.auth.views import LoginView, LogoutView
from users.forms import LoginForm

class UserLogin(LoginView):
	authentication_form=LoginForm
	template_name='users/login.html'

class UserLogout(LogoutView):
	template_name='users/logout.html'

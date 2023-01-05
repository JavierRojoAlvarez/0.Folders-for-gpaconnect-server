from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
class LoginRequiredUrlMixin(LoginRequiredMixin):
	login_url=reverse_lazy('login')

class ActiveMixin:
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		active_keys=self.active_keys
		if active_keys:
			for key in active_keys:
				context[key]='active'
		return context

class TrackerTemplateView(LoginRequiredUrlMixin,TemplateView):
	template_name='tracker/tracker.html'

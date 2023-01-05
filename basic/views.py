from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class ActiveMixin:
	'''Add items to context dictionary with a value of active for chosen keys'''
	active_keys = None

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		active_keys = self.active_keys
		if active_keys:
			for key in active_keys:
				context[key] = 'active'
		return context


class LoginRequiredUrlMixin(LoginRequiredMixin):
	login_url = reverse_lazy('login')


class HomeTemplateView(ActiveMixin, LoginRequiredUrlMixin, TemplateView):
	template_name = 'basic/home.html'
	active_keys = ['home_template_active']


class TestTemplateView(TemplateView):
	template_name = 'basic/test.html'
	login_url = reverse_lazy('login')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if self.request.POST:
			context['parentform'] = TransactionForm(self.request.POST)
			context['formset'] = EntryFormSet(self.request.POST)
		else:
			context['parentform'] = TransactionForm()
			initial_data = [{'direction': 1}, {'direction': 2}]
		return context


class ServicesTemplateView(ActiveMixin, LoginRequiredUrlMixin, TemplateView):
	template_name = 'basic/services.html'
	active_keys = ['services_template_active']


class ContactTemplateView(ActiveMixin, LoginRequiredUrlMixin, TemplateView):
	template_name = 'basic/contact.html'
	active_keys = ['contact_template_active', 'info_active']


class AboutTemplateView(ActiveMixin, LoginRequiredUrlMixin, TemplateView):
	template_name = 'basic/about.html'
	active_keys = ['about_template_active', 'info_active']

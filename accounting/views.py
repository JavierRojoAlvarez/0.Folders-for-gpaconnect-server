from django.shortcuts import render

from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import simplejson as json
from itertools import repeat

from my_app.models import *

from django.db.models import *
from django.urls import reverse_lazy

from django.shortcuts import get_object_or_404

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope, OAuth2Authentication



from decimal import Decimal, ROUND_HALF_UP
import datetime

today=datetime.date.today().strftime("%d/%m/%Y")

class LoginRequiredUrlMixin(LoginRequiredMixin):
	login_url=reverse_lazy('login')

class ActiveMixin:
	active_keys=None
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		active_keys=self.active_keys
		if active_keys:
			for key in active_keys:
				context[key]='active'
		return context

class StatementsTemplateView(ActiveMixin,LoginRequiredUrlMixin,TemplateView):
	template_name='accounting/statements.html'
	active_keys=['accounting_active']


	def get_context_data(self,**kwargs):
		date_threshold=datetime.datetime(2022,1,1)

		current_asset_kwargs={'account__description':'Bank Account','transaction__date__lte':date_threshold}
		non_current_asset_kwargs={'account__description':'Buildings Cost','transaction__date__lte':date_threshold}
		non_current_liability_kwargs={'account__description':'Deferred Expense (Lease)','transaction__date__lte':date_threshold}
		income_kwargs={'account__description':'Rent Recovery','transaction__date__lte':date_threshold}
		expenditure_kwargs={'account__description':'Rent Expenditure','transaction__date__lte':date_threshold}
		equity_kwargs={'account__description':'OB General Fund','transaction__date__lte':date_threshold}
		is_actual=False

		def get_total(**kwargs):
			if is_actual:
				actual_kwarg={'transaction__actual_expected':'A'}
				kwargs={**kwargs,**actual_kwarg}
			qs=Entry.objects.filter(**kwargs)
			grand_total=sum((entry.signed_amount for entry in qs))
			def signed_amount():
				lhs = ['Buildings Cost', 'Rent Expenditure', 'Bank Account']
				rhs = ['Deferred Expense (Lease)','Rent Recovery','OB General Fund']
				lhs_debit=When(Q(direction__name='Debit') & Q(account__description__in=lhs), then=F('amount'))
				lhs_credit=When(Q(direction__name='Credit') & Q(account__description__in=lhs), then=F('amount')*(-1))
				rhs_debit=When(Q(direction__name='Debit') & Q(account__description__in=rhs), then=F('amount')*(-1))
				rhs_credit=When(Q(direction__name='Credit') & Q(account__description__in=rhs), then=F('amount'))
				output=Case(lhs_debit,lhs_credit,rhs_debit,rhs_credit)
				return output
			qs=qs.values('account__description').annotate(subtotal=Sum(signed_amount()))
			qs.grand_total=grand_total
			return qs
		income_statement = [{'title':'Operating',
							'data':[{'label':'Income','qs':get_total(**income_kwargs)},
									{'label':'Expenditure','qs':get_total(**expenditure_kwargs)}]
							}]
		balance_sheet = [
							{'title':'Assets',
							'data':[{'label':'Current','qs':get_total(**current_asset_kwargs)},
									{'label':'Non Current','qs':get_total(**non_current_asset_kwargs)}]
							},
							{'title':'Liabilities',
							'data':[{'label':'Current','qs':None},
									{'label':'Non Current','qs':get_total(**non_current_liability_kwargs)}]
							},
							{'title':'Equity',
							'data':[{'label':'General Fund','qs':get_total(**equity_kwargs)}]
							}
						]
		valid_statements=['pl','balance_sheet']
		try:
			statement_param=self.request.GET['statement']

		except:
			active_statement='pl'
		else:
			if statement_param in valid_statements:
				active_statement=statement_param
			else:
				active_statement='pl'

		active_dict = {active_statement+'_active':'active',
						active_statement+'_show':'show'}
		context = {
					'date_threshold':date_threshold,
					'balance_sheet':balance_sheet,
					'income_statement':income_statement,
				}
		context={**context,**active_dict,'accounting_active':'active'}
		print(context)
		return context

import os
from django.template.loader import get_template
from html import escape
from website import settings
from django.http import  HttpResponse, FileResponse, Http404
from invoice.models import *
from invoice.forms import *
from my_app.models import *
from invoice.pdf import *

from django.core.files.base import File, ContentFile
from django.core.files.uploadedfile import *

from django.views.generic.edit import CreateView, DeleteView, UpdateView

import simplejson as json

def preview_pdf(request):
	payload=json.load(request)
	print(payload)
	form=IssuedInvoiceForm(payload)
	form.is_valid()
	print(form.cleaned_data)
	context = {'pagesize':'A4', **form.cleaned_data}
	pdf_file = make_pdf_preview('invoice/invoice.html', context, as_preview=True)
	try:
		response = HttpResponse(pdf_file, content_type='application/pdf')
	except:
		raise Http404()
	return response

class ReceivedInvoiceCreateView(CreateView):
	success_url = reverse_lazy('contract-list')

	def is_issuer(self):
		'''Return True if GPA is issuing invoice and False if receiving'''
		payment = self.get_payment()
		contract_type_name = payment.contract.contract_type.name
		if contract_type_name == 'Sublease':
			return True
		else:
			return False

	def get_form_class(self):
		if self.is_issuer():
			form_class = IssuedInvoiceForm
		else:
			form_class = ReceivedInvoiceForm
		return form_class

	def get_payment(self):
		'''Return the associated contract payment record'''
		try:
			payment_id = self.kwargs['pk']
			return ContractPayment.objects.get(id=payment_id)
		except:
			return None

	def get_context_data(self,**kwargs):
		context = super().get_context_data(**kwargs)
		context['payment'] = self.get_payment()
		return context

	def get_form_kwargs(self):
		form_kwargs = super().get_form_kwargs()
		print('Form kwargs original:',form_kwargs)
		try:
			files = form_kwargs['files']
			pdf = files['pdf']
			print('Dir:',dir(pdf))
			content = pdf.file
			field_name=pdf.field_name
			size=pdf.size
			charset=pdf.charset
			print('Content:',content)
			print('Field Name:',field_name)
			print('Size:',size)
			print('Charset:',charset)
			print(type(content))
		except:
			pass
		try:
			data = form_kwargs['data'].copy()
			data['associated_payment'] = self.get_payment().id
			form_kwargs['data'] = data
			print(form_kwargs['data'])
		except Exception as e:
			print(e)
		return form_kwargs

	def form_valid(self,form):
		success_url=super().form_valid(form)
		self.make_records(form)
		return success_url

	def get_transaction_kwargs(self,form):
		'''Get transaction kwargs from the form's cleaned data. The transaction
		type used (e.g. Send Invoice) is determined from the contract type.'''
		if self.is_issuer():
			transaction_type_name = 'Send Invoice'
		else:
			transaction_type_name = 'Create Invoice Receipt'
		transaction_type=TransactionType.objects.get(name=transaction_type_name)
		data=form.cleaned_data
		print('Cleaned data:',data)
		associated_payment=data['associated_payment']
		contract=associated_payment.contract
		try:
			date=data['date_received']
		except:
			date=data['date_issued']

		transaction_kwargs = {
			'transaction_type':transaction_type,
			'amount':data['amount'],
			'date': date,
			'treatment':'Accounting',
			'contract': contract,
			'actual_expected': 'A'
		}
		print('Transaction Kwargs:',transaction_kwargs)
		return transaction_kwargs

	def make_records(self, form):
		'''Make transaction and entry records using transaction kwargs'''
		transaction_kwargs=self.get_transaction_kwargs(form)
		transaction=Transaction(**transaction_kwargs)
		transaction.save()
		print(transaction)
		pseudoentry_set=transaction.transaction_type.pseudoentry_set.values()
		entry_list=[]
		print('Building entries...')
		for entry in pseudoentry_set:
			entry.pop('id')
			entry.pop('transaction_type_id')
			entry['amount']=transaction.amount
			entry['transaction']=transaction
			entry_list.append(Entry(**entry))
			print(entry)
		print('\n')
		Entry.objects.bulk_create(entry_list)
		print('Saved entries')
		payment=self.get_payment()
		payment.actual_expected='A'
		payment.save()
		print('Set payment to actual')


	def get_success_url(self):
		url=super().get_success_url()
		try:
			url=self.request.POST.get('next')
		except Exception as e:
			print(e)
		return url

	def get_template_names(self):
		if self.is_issuer():
			template='invoice/received-invoice/issued-invoice-create.html'
		else:
			template='invoice/received-invoice/received-invoice-create.html'
		return [template]

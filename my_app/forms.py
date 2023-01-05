from django import forms
from django.forms import ModelForm
from .models import *
from django.forms import inlineformset_factory, modelformset_factory
from website.settings import DATE_INPUT_FORMATS
from django.forms.models import BaseInlineFormSet, _get_foreign_key, BaseModelFormSet, modelform_factory, BaseFormSet
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


reg_attrs={'class':'form-control form-control-md rounded'}
check_attrs={'class': 'form-control form-control-sm','style':'width: 1.5rem;'}
date_attrs={'class':'form-control form-control-md rounded date-input','name':'date'}
req_attrs={'required': 'required'}


class BuildingForm(ModelForm):
	class Meta:
		model = Building
		widgets = {
		'epims_id': forms.TextInput(attrs=reg_attrs),
		'name': forms.TextInput(attrs=reg_attrs),
		'region': forms.Select(attrs=reg_attrs),
		'nia': forms.NumberInput(attrs=reg_attrs),
		'ftes_capacity': forms.NumberInput(attrs=reg_attrs),
		'image':forms.FileInput(attrs={'class': 'form-control-file'})
		}
		fields=list(widgets.keys())

class CostForm(ModelForm):
	class Meta:
		model = Cost
		widgets = {
		'cost_type': forms.Select(attrs=reg_attrs),
		'building': forms.Select(attrs=reg_attrs),
		'value': forms.TextInput(attrs=reg_attrs),
		'start': forms.DateInput(attrs=reg_attrs),
		'end': forms.DateInput(attrs=reg_attrs),
		}
		fields=list(widgets.keys())

class EntryForm(ModelForm):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

	class Meta:
		model=Entry
		widgets = {
		'direction': forms.Select(attrs={**reg_attrs,**req_attrs}),
		'transaction': forms.Select(attrs={**reg_attrs,**req_attrs}),
		'account': forms.Select(attrs={**reg_attrs,**req_attrs}),
		'amount': forms.NumberInput(attrs={'class':'form-control form-control-md rounded amount','required':'required'}),
		}
		fields=list(widgets.keys())

class EntryContractForm(ModelForm):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

	class Meta:
		model=Entry
		widgets = {
		'direction': forms.Select(attrs={**reg_attrs,**req_attrs}),
		'contract': forms.Select(attrs={**reg_attrs,**req_attrs}),
		'account': forms.Select(attrs={**reg_attrs,**req_attrs}),
		'amount': forms.NumberInput(attrs={'class':'form-control form-control-md rounded amount'}),
		}
		fields=list(widgets.keys())

class TransactionForm(ModelForm):
	def __init__(self, *args,initial_data=None, nested_data=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.initial_data=initial_data
		self.nested_data=nested_data
	class Meta:
		model=Transaction
		widgets = {
		'transaction_type':forms.Select(attrs=reg_attrs),
		'date': forms.DateInput(format=DATE_INPUT_FORMATS[0], attrs=date_attrs),
		'contract':forms.Select(attrs=reg_attrs),
		'period': forms.TextInput(attrs={'class':'form-control form-control-md rounded','placeholder': 'Period'}),
		'amount':forms.NumberInput(attrs={'class':'form-control form-control-md rounded amount','placeholder': 'Amount'}),
		'actual_expected': forms.Select(attrs=reg_attrs),

		}
		fields=list(widgets.keys())

class ContractPaymentForm(ModelForm):
	def __init__(self, *args,initial_data=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.initial_data=initial_data
	class Meta:
		model=ContractPayment
		widgets = {
		'transaction_type':forms.Select(attrs=reg_attrs),
		'date': forms.DateInput(format=DATE_INPUT_FORMATS[0], attrs=date_attrs),
		'contract':forms.Select(attrs=reg_attrs),
		'period': forms.TextInput(attrs={'class':'form-control form-control-md rounded','placeholder': 'Period'}),
		'amount':forms.NumberInput(attrs={'class':'form-control form-control-md rounded amount','placeholder': 'Amount'}),
		'actual_expected': forms.Select(attrs=reg_attrs)
		}
		fields=list(widgets.keys())
class ContractForm(ModelForm):
	sort_by_fields=['start','end','organisation']
	filter_fields=['revenue_expenditure','contract_type','organisation',
					'start','end','signed']
	filter_groups=[
					['revenue_expenditure','contract_type'],
					['organisation','signed'],
					['building'],
				]
	class Meta:
		model=Contract
		widgets = {
		'revenue_expenditure':forms.Select(attrs=reg_attrs),
		'contract_type':forms.Select(attrs=reg_attrs),
		'organisation':forms.Select(attrs=reg_attrs),
		'building':forms.SelectMultiple(attrs={'class':'form-control form-control-md rounded selectpicker','title':"Select any number of buildings",'data-actions-box':"true",'data-live-search':"true"}),
		# 'treatment':forms.Select(attrs=reg_attrs),
		# 'start': forms.DateInput(format=DATE_INPUT_FORMATS, attrs=date_attrs),
		# 'end': forms.DateInput(format=DATE_INPUT_FORMATS, attrs=date_attrs),
		'description':forms.TextInput(attrs=reg_attrs),
		'signed': forms.CheckboxInput(attrs=check_attrs)
		}
		fields=list(widgets.keys())




class BaseEntryFormset(BaseInlineFormSet):
	def __init__(self, *args, **kwargs):
		super().__init__(*args,**kwargs)
	def get_form_kwargs(self, form_index):
		form_kwargs = super().get_form_kwargs(form_index)
		try:
			nested_data=form_kwargs['nested_data']
			if form_index<len(nested_data):
				form_kwargs['initial_data']=nested_data[form_index]
			else:
				form_kwargs['initial_data']=[{'direction':1},{'direction':2}]
		except Exception as e:
			print(e)
		return form_kwargs

	def add_fields(self, form, index):
		super().add_fields(form, index)
		nested = EntryFormSet(
						data=form.data if form.is_bound else None,
						instance=form.instance,
						initial=form.initial_data,
						files=form.files if form.is_bound else None,
						prefix='entry-%s-%s' % (
							form.prefix,
							EntryFormSet.get_default_prefix()),
						)
		nested.extra=2
		form.nested=nested
	def clean(self):
		"""
		If a parent form has no data, but its nested forms do, we should
		return an error, because we can't save the parent.
		For example, if the TransactionForm is empty, but there are Entries.
		"""
		for form in self.forms:
			if form.cleaned_data=={}:
				form.add_error(field=None,error='Form is empty. Please fill')

	def _is_adding_nested_inlines_to_empty_form(self, form):
		"""
		Are we trying to add data in nested inlines to a form that has no data?
		e.g. Adding Images to a new Book whose data we haven't entered?
		"""
		if not hasattr(form, 'nested'):
			# A basic form; it has no nested forms to check.
			return False

		# if is_form_persisted(form):
			# We're editing (not adding) an existing model.
			# return False

		if not is_empty_form(form):
			# The form has errors, or it contains valid data.
			return False

		# All the inline forms that aren't being deleted:
		non_deleted_forms = set(form.nested.forms).difference(
			set(form.nested.deleted_forms)
		)

		# At this point we know that the "form" is empty.
		# In all the inline forms that aren't being deleted, are there any that
		# contain data? Return True if so.
		return any(not is_empty_form(nested_form) for nested_form in non_deleted_forms)
	def save(self, commit=True):
		result = super().save(commit=commit)

		for form in self.forms:
			if hasattr(form, 'nested'):
				if not self._should_delete_form(form):
					form.nested.save(commit=commit)

		return result

EntryFormSet=inlineformset_factory(Transaction,Entry,form=EntryForm, can_delete=False)
TransactionFormSet=inlineformset_factory(Contract,Transaction,form=TransactionForm,can_delete=False)
ContractPaymentFormSet=inlineformset_factory(Contract,ContractPayment,form=ContractPaymentForm,can_delete=False)
EntryContractFormSet=inlineformset_factory(Contract,Entry,form=EntryContractForm, can_delete=False)

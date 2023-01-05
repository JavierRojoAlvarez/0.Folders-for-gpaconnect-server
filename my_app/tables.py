import django_tables2 as tables
from django_tables2.tables import Table
from django.utils.html import format_html
from .calculate import *


class CalculationTable(Table):
	name=tables.TemplateColumn('<a href="{% url "building-detail" record.building %}">{{value}}</a>')
	fy_start=tables.Column()
	cost_type=tables.Column()
	value_norm =tables.TemplateColumn('<a href="{% url "building-detail" record.building %}">£{{ record.value_norm|floatformat:2 }}</a>')

class CostSetTable(Table):
	cost_type=tables.Column()
	start=tables.Column()
	end=tables.Column()
	value=tables.TemplateColumn('{% load humanize %} £{{ record.value|floatformat:2|intcomma }}')
	view=tables.TemplateColumn('<a href="{% url "cost-detail" record.id %}" class="btn btn-sm btn-outline-success border-0" role="button"><i class="fas fa-eye"></i></a>')
	edit=tables.TemplateColumn('<a href="{% url "cost-update" record.id %}" class="btn btn-sm btn-outline-info border-0" role="button"><i class="far fa-edit"></i></a>')
	delete=tables.TemplateColumn('<a href="{% url "cost-delete" record.id %}" class="btn btn-sm btn-outline-danger border-0" role="button"><i class="far fa-trash-alt"></i></a>')

class CostSetGroupbyTable(Table):
	cost_type__name=tables.Column()
	value__sum=tables.TemplateColumn('{% load humanize %} £{{ record.value__sum|floatformat:2|intcomma }}')

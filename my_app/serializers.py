from .models import *
from rest_framework import serializers

class CostSerializer(serializers.ModelSerializer):
	class Meta:
		model = Cost
		fields = '__all__'

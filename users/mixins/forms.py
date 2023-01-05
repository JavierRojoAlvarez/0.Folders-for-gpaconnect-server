class FormAttrMixin:
	reg_attrs={'class':'form-control form-control-md rounded'}
	username_attrs=dict({'placeholder':'Username'},**reg_attrs)
	password_attrs=dict({'placeholder':'Password'},**reg_attrs)

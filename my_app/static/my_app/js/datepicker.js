function addDatePicker() {
	var dateInputs=$('.date-input');
	var container=$('.bootstrap-iso form').length>0 ? $('.bootstrap-iso form').parent() : "body";
	dateInputs.datepicker({
			format: 'dd/mm/yyyy',
			container: container,
			todayHighlight: true,
			autoclose: true,
	}).on('changeDate', getDateLimits);
};
$(document).ready(
	addDatePicker
);

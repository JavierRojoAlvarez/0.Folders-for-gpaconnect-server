let amountInput = document.getElementById('id_amount');
let pseudoSelect = document.getElementById('id_transaction_type');
let addBtn = document.getElementById('btn-add');
let formsetDiv = document.getElementById('formset');
let tokenVal = document.getElementsByName('csrfmiddlewaretoken')[0].value;

function makeDecimal() {
	amountInput.value = parseFloat(parseFloat(amountInput.value).toFixed(2));
};

function getFormsetValues() {
	var fieldElements = formsetDiv.querySelectorAll('#formset input, select');
	let myObj = {};
	for (var element of fieldElements.values()) {
		myObj[element.name] = element.value;
	};
	console.log('Current formset values...');
	console.log(myObj);
	return JSON.stringify(myObj);
};

function removeRowListener() {
	document.querySelectorAll('.btn-remove-row').forEach(function(el) {
		el.addEventListener('click', function() {
			getFormset(null, this.id, null, null);
			console.log('Removed row at index: ' + this.id);
		});
	});
};


function getFormset(addEntry, removeEntryIndex, amountDecimal, transactionTypeId) {
	console.log('%c getFormset() Initiated','background: cornflowerblue;\
		color: white; padding: 2px; border-radius:2px');
	fetch('/transaction/formset', {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'X-CSRFToken': tokenVal
		},
		body: JSON.stringify({
			amount:amountDecimal,
			parent_type:transactionTypeId,
			add_entry:addEntry,
			remove_entry:removeEntryIndex,
			current_data:JSON.parse(getFormsetValues())
		}),
		credentials:'same-origin'
	}).then(response => response.text())
		.then(function(html_data) {
			document.getElementById('formset').innerHTML = html_data;
			removeRowListener();
			addDatePicker();
			console.log('%c getFormset() Successful','background: mediumseagreen;\
				color: white; padding: 2px; border-radius:2px');
		})
		.catch(error => console.log(error))
};

amountInput.addEventListener('input', function() {
	getFormset(null, null, amountInput.value, null);
	makeDecimal();
});

pseudoSelect.addEventListener('change', function() {
	getFormset(null, null, amountInput.value, pseudoSelect.value);
});

addBtn.addEventListener('click', function() {
	getFormset(true, null, null, null);
});

removeRowListener();

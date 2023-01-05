var endpoint;
let amountInput = document.getElementById('id_amount');
let addBtn = document.getElementById('btn-add');
let formsetDiv = document.getElementById('formset');
let tokenVal = document.getElementsByName('csrfmiddlewaretoken')[0].value;
let pseudoSelect = document.getElementById('id_transaction_type');


function getDateLimits() {
	let startDate = document.getElementById('start-date');
	let endDate = document.getElementById('end-date');
	let dateInputs = formsetDiv.querySelectorAll('.date-input');
	if (startDate && endDate && dateInputs) {
		var dates=[];
		for (let date of dateInputs.values()) {
			if (!dates.includes(date.value)) {
				dates.push(date.value);
			};
		};
		var moment_dates=[];
		for (let date of dates) {
			moment_date=moment(date, 'DD/MM/YYYY')
			if (moment_date.isValid()) {
				moment_dates.push(moment_date);
			};
		};
		let minDate=moment.min(moment_dates);
		let maxDate=moment.max(moment_dates);
		if (moment_dates.length === 0) {
			startDate.innerHTML='- - -';
			endDate.innerHTML='- - -';
		} else {
			startDate.innerHTML=minDate.format('Do MMMM YYYY');
			endDate.innerHTML=maxDate.format('Do MMMM YYYY');
		};
	};
};

function dateListener() {
	formsetDiv.querySelectorAll('.date-input').forEach(function(el) {
		el.addEventListener('input', function() {
			getDateLimits();
		});
	});
};


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

function changeTransactionAmounts() {
	var elems = formsetDiv.querySelectorAll('.amount');
	var index = 0, length = elems.length;
	console.log(amountInput.value)
	for ( ; index < length; index++) {
			elems[index].value=amountInput.value;
	};
	console.log('Changed amounts in formset');
};

if (document.body.contains(document.getElementById('formset2'))) {
	formset2Div = document.getElementById('formset2')
	function changeEntryAmounts() {
		var amountInputs = formset2Div.querySelectorAll('.amount');
		let total=getTransactionAmounts()
		for (var amountInput of amountInputs.values()) {
			amountInput.value=total;
		};
		console.log('Changed entry values');
	};
	changeEntryAmounts();
};

function getTransactionAmounts() {
	var transactionAmountInputs=formsetDiv.querySelectorAll('.amount');
	let total=0.00
	for (var transactionAmountInput of transactionAmountInputs.values()) {
		console.log(transactionAmountInput.value);
		total += parseFloat(transactionAmountInput.value);
	}
	console.log('Transaction amount total: ' + total);
	return total.toFixed(2)
};



function transactionAmountListener() {
	var transactionAmountInputs=formsetDiv.querySelectorAll('.amount');
	for (var el of transactionAmountInputs.values()) {
		el.addEventListener('input',changeEntryAmounts);
	};
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
	fetch(endpoint, {
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
			transactionAmountListener();
			if (changeEntryAmounts) {
				changeEntryAmounts()
			};
			removeRowListener();
			addDatePicker();
			dateListener();
			getDateLimits();
			console.log('%c getFormset() Successful','background: mediumseagreen;\
				color: white; padding: 2px; border-radius:2px');
		})
		.catch(error => console.log(error))
};

amountInput.addEventListener('input', function() {
	makeDecimal();
	changeTransactionAmounts();
});

addBtn.addEventListener('click', function() {
	getFormset(true, null, null, null);
});

if (pseudoSelect) {
	pseudoSelect.addEventListener('change', function() {
		getFormset(null, null, amountInput.value, pseudoSelect.value);
	});
};

function doubler(num) {
	console.log(num*2);
};
removeRowListener();
transactionAmountListener();
dateListener();
getDateLimits();

let endpoint = '/invoice/preview/';
let tokenVal = document.getElementsByName('csrfmiddlewaretoken')[0].value;
let previewBtn = document.getElementById('previewBtn');
let formDiv = document.getElementById('form');

previewBtn.addEventListener('click', showPreview);
function showPreview() {
	getPreview();
};

function getFormValues() {
	var fieldElements = formDiv.querySelectorAll('#form input, select');
	let myObj = {};
	for (var element of fieldElements.values()) {
		myObj[element.name] = element.value;
	};
	console.log('Current form values...');
	console.log(myObj);
	return JSON.stringify(myObj);
};

function getPreview(addEntry, removeEntryIndex, amountDecimal, transactionTypeId) {
	console.log('%c getPreview() Initiated','background: cornflowerblue;\
		color: white; padding: 2px; border-radius:2px');
	fetch(endpoint, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'X-CSRFToken': tokenVal
		},
		body: getFormValues()
		,
		credentials:'same-origin'
	}).then(response => response.blob())
		.then(function(myBlob) {
			console.log(typeof myBlob);
			var objectURL = URL.createObjectURL(myBlob);
			window.open(objectURL, 'Preview Invoice');
			console.log('%c getPreview() Successful','background: mediumseagreen;\
				color: white; padding: 2px; border-radius:2px');
		})
		.catch(error => console.log(error))
};

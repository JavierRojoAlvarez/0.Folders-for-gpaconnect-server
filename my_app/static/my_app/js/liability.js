var endpoint = '/api/liability';
let id=document.getElementById('id').value

function successfn(response) {
	var line_ctx = document.getElementById('myLine').getContext('2d');
	var datasetArray=[]
	for (let dataset of response.datasets) {
		console.log(dataset.series);
		console.log(dataset.label);
		datasetArray.push({
								label: dataset.label,
								borderColor: 'rgb(255, 99, 132)',
								pointBackgroundColor: 'rgb(255, 99, 132)',
								data: dataset.series,
								lineTension: 0
		});
	};
	var dataObj = {
		labels: response.labels,
		datasets: datasetArray,
	};
	var lineChart = new Chart (line_ctx, {
		type:'line',
		data:dataObj,
	});
	document.getElementById('spinner').style.display = 'none';
	document.getElementById('source').style.display = 'block';
	console.log('Request successful!');
};


console.log('%c Making API request...','background: cornflowerblue;\
	color: white; padding: 2px; border-radius:2px');
fetch(endpoint+'?id='+id, {
	method: 'GET',
	headers: {
		'Accept': 'application/json',
	},
	credentials:'same-origin'
}).then(response => response.json())
	.then(successfn)
	.catch(error => console.log(error))

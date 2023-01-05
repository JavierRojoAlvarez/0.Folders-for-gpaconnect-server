var line_endpoint = '/api/line';

function successfn(data) {
	data.labels= data.labels.map(dateString => new moment(dateString));

	var line_ctx = document.getElementById('myLine').getContext('2d');
	function userCallbackfn(value, index, values) {
		return value.toLocaleString();
	}
	var yAxes =	[{
		ticks: {beginAtZero: true, userCallback: userCallbackfn}
	}]
	var xAxes = [{
		type: 'time',
		gridLines: {display:true},
		time: {minUnit: 'month'}
	}]
	var dataObj = {
		labels: data.labels,
		datasets: [{
								label: 'UK Total Covid-19 Cases ',
								borderColor: 'rgb(255, 99, 132)',
								pointBackgroundColor: 'rgb(255, 99, 132)',
								data: data.values
		}]
	}
	var optionsObj = {
		scales: {
						xAxes: xAxes,
						yAxes: yAxes
		}
	}
	var lineChart = new Chart (
		line_ctx,
		{type:'line', data:dataObj, options:optionsObj}
	);
	document.getElementById('spinner').style.display = 'none';
	document.getElementById('source').style.display = 'block';
	console.log('Request successful!');
};


console.log('Request initiated to endpoint: '+line_endpoint);
$.ajax({
	method: "GET",
	url: line_endpoint,
	success: successfn,
	error: function(error_data) {	console.log(error_data) }
});


var pie_ctx = document.getElementById('myPie').getContext('2d');
var pieChart = new Chart(pie_ctx, {
	type: 'pie',
	data: {
		labels: ['GPA','OGD', 'BBQ'],
		datasets: [{
				label: 'Finance Numbers',
				backgroundColor: [
					'rgb(187, 29, 250)',
					'rgb(255, 99, 132)',
					'rgb(28, 199, 132)'
				],
				data: [2, 10, 5]
		}]
	},
	options: {}
});

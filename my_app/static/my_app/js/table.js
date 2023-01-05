let query_url = window.location.search;
let api='/api/cheese/';
let api_url=api+query_url;
console.log(query_url);
console.log(api_url);


$('#table').bootstrapTable({
	url: api_url,
	showColumns: true,
	sortReset:true,
	showRefresh: true,
	showFullscreen: true,
	pagination: true,
	search: true,
	columns: [{
			field: 'fy_string',
			title: 'FY'
		}, {
			field: 'name',
			title: 'Name',
			sortable: 'true',
			formatter: function (value) {
				var url = "{% url 'building-list' %}";
				return '<a href="/building/list">'+value+'</a>'
			}
		}, {
			field: 'value_norm',
			title: 'Value',
			sortable: 'true',
			formatter: function (value) {
							return value.toLocaleString('en-GB', {
													style: 'currency',
													currency: 'GBP',
												})
						}
		}]
	})

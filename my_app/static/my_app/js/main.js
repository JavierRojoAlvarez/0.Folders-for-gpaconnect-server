$(document).ready(function() {
		$('.my_table').DataTable( {
				"paging":false,
				"info":false,
				"dom": '<t>'
		} );
} );
$('#my_search').on('keyup change', function () {
	$('.my_table').DataTable().search(this.value).draw();
});

function show_overlay(){
		$('#loading_overlay').removeClass('d-none');
	};
function hide_overlay(){
		$('#loading_overlay').addClass('d-none');
};
function iframe_has_loaded(){
	$(window).onload(setTimeout(hide_overlay,1000));
};
setTimeout(show_overlay,100);
var iframe_present=false
if ($('iframe').length > 0){
	iframe_present=true;
};
if (iframe_present==false){
	$(window).onload(setTimeout(hide_overlay,100));
};

var el = document.querySelector('#id_cost_value');
el.addEventListener('keyup', function (event) {
	if (event.which >= 37 && event.which <= 40) return;
	this.value = this.value.replace(/\D/g, '')
							.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
});

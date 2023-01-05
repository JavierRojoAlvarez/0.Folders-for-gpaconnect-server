function reset(fieldId){
	document.getElementById(fieldId).selectedIndex=0;
};

document.getElementById("resetBtnRegion").addEventListener("click", function(){
	reset('region');
});
document.getElementById("resetBtnSort").addEventListener("click", function(){
	reset('sort_by');
});
document.getElementById("resetBtnAll").addEventListener("click", function(){
	reset('region');
	reset('sort_by');
});

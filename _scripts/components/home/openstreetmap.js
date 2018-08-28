function openstreetmap() {
    var kkmap = L.map('start65',
		      {scrollWheelZoom: false,
		       dragging: false}
		     ).setView([50.746403, 4.257978], 16);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
		{attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}
	       ).addTo(kkmap);
    
    L.marker([50.7466, 4.2576]).addTo(kkmap);
}

$(document).ready(function(){
    openstreetmap();
});

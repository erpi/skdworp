function openstreetmap() {
    var nimap = L.map('oudKasteel',
		      {scrollWheelZoom: false,
		       dragging: false}
		     ).setView([50.71942, 4.2568], 16);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
		{attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}
	       ).addTo(nimap);
    
    L.marker([50.71948, 4.2568]).addTo(nimap);
}

$(document).ready(function(){
    openstreetmap();
});

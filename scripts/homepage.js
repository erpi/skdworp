---
# http://www.grall.name/posts/1/antiSpam-emailAddressObfuscation.html
# http://www.grall.name/posts/1/onlineTools_obfuscation.html

# http://stackoverflow.com/questions/4531052/how-can-i-disable-scrolling-on-the-google-maps-mobile-layout
---
function googleMapsInitialize() {
  var LatLngKK = new google.maps.LatLng(50.746403, 4.257978);
  var LatLngNI = new google.maps.LatLng(50.740465, 4.242809);
  var mapOptionsKK = {
    zoom: 15,
    center: LatLngKK,
    mapTypeId:google.maps.MapTypeId.ROADMAP,
    disableDefaultUI: true,
    draggable: false,
		scrollwheel: false,
    clickableIcons: false,
  };
  var mapOptionsNI = {
    zoom: 15,
    center: LatLngNI,
    mapTypeId:google.maps.MapTypeId.ROADMAP,
    disableDefaultUI: true,
    draggable: false,
		scrollwheel: false,
    clickableIcons: false,
  };
  var mapKK = new google.maps.Map(document.getElementById("start65"),mapOptionsKK);
  var mapNI = new google.maps.Map(document.getElementById("campus"),mapOptionsNI);
  var markerKK = new google.maps.Marker({
    position: LatLngKK,
    map: mapKK,
    title: 'turncentrum start65'
  });
  var markerNI = new google.maps.Marker({
    position: LatLngNI,
    map: mapNI,
    title: 'campus halle'
  });
};

function smoothScrolling() {
  // Add smooth scrolling to all links in navbar
  $(".navbar a[href*='#over-ons'], header div div a, #lok1, #best1").on('click', function(event) {
    // Prevent default anchor click behavior
    event.preventDefault();
    // Store hash
    var hash = this.hash;
    // Using jQuery's animate() method to add smooth page scroll
    $('html, body').animate({
      scrollTop: $(hash).offset().top
    }, 1000, function(){
      // Add hash (#) to URL when done scrolling (default click behavior)
      window.location.hash = hash;
    });
  });
};

function decrypt(origin, size, key, word) {
  var s = 0
  for (var i = 0; i < key.length; i++) {
    s = s + key.charCodeAt(i)
  }
  var pos = 0
  var first = s % word.length
  var prefix = ''
  var suffix = ''
  for (var i = 0; i < word.length - first; i++) {
    suffix = suffix + String.fromCharCode((word.charCodeAt(i) + size - key.charCodeAt(pos)) % size+ origin)
    pos = (pos + 1) % key.length
  }
  for (var i = word.length - first; i < word.length; i++) {
    prefix = prefix + String.fromCharCode((word.charCodeAt(i) + size - key.charCodeAt(pos)) % size + origin)
    pos = (pos + 1) % key.length
  }
  var d = prefix + suffix
  return d;
};

$(document).ready(function(){
    smoothScrolling();
    $(".encrypted").text(function(i, origText){
        var zonder_dubbele_slash = origText.replace("\\\\", "\\");
        return "  " + decrypt(46, 77, "schaken", zonder_dubbele_slash);
    });
});

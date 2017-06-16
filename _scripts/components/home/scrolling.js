function smoothScrolling() {
  // Add smooth scrolling to all links in navbar
  $(".navbar a[href*='#over-ons'], #btn-over, #lok1, #best1").on('click', function(event) {
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
}

$(document).ready(function(){
    smoothScrolling();
});

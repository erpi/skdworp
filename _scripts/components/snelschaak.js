$(document).ready(function(){
  $('.stand-snelschaak > tbody  > tr').each(function() {
    var uitslagen = [];
    $(this).children('td').slice(2, -1).each(function(index, td) {
      var uitslag = [parseFloat($(td).html()), td];
      if (Number.isFinite(uitslag[0])) {
        uitslagen.push(uitslag);
      }
    });
    if (uitslagen.length > 5) {
      uitslagen.sort(function(a, b) {return b[0] - a[0];});
      for (var i = 5; i < uitslagen.length; i++) {
        // console.log(uitslagen[i][0]);
        $(uitslagen[i][1]).addClass('doorstreept');
      }
    }
  });
});

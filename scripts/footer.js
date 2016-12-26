function naarBoven() {
  $("html, body").animate({ scrollTop: 0 }, 1000);
  return false;
};

function setFooterStyle() {
  var docHeight = $(window).height();
  var footerHeight = $('#footer').outerHeight();
  var footerTop = $('#footer').position().top + footerHeight;
  if (footerTop < docHeight) {
      $('#pijl').addClass('invisible');
      $('#footer').css('margin-top', (docHeight - footerTop) + 'px');
  } else if (footerTop < 1.3 * docHeight) {
      $('#pijl').addClass('invisible');
      $('#footer').css('margin-top', '');
  } else {
      $('#pijl').removeClass('invisible');
      $('#footer').css('margin-top', '');
  }
  $('#footer').removeClass('invisible');
};

$(document).ready(function(){
  setFooterStyle();
  window.onresize = setFooterStyle;
  $('a[data-toggle="pill"]').on('shown.bs.tab', setFooterStyle);
});

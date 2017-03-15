$(document).ready(function(){
  // extra velden op basis van type verslag
  $("#interclubs-info").css('display', ($('#type-verslag').attr("value") == 'ni') ? 'block' : 'none');
  $("#kk-info").css('display', ($('#type-verslag').attr("value") == 'kk') ? 'block' : 'none');
  $("#help-tag-ni").css('display', ($('#type-verslag').attr("value") == 'ni') ? 'block' : 'none');
  $("#help-tag-kk").css('display', ($('#type-verslag').attr("value") == 'kk') ? 'block' : 'none');
  $("#help-tag-varia").css('display', ($('#type-verslag').attr("value") == 'varia') ? 'block' : 'none');
  $('#type-verslag').on('change', function () {
    $("#interclubs-info").css('display', (this.value == 'ni') ? 'block' : 'none');
    $("#kk-info").css('display', (this.value == 'kk') ? 'block' : 'none');
    $("#help-tag-ni").css('display', (this.value == 'ni') ? 'block' : 'none');
    $("#help-tag-kk").css('display', (this.value == 'kk') ? 'block' : 'none');
    $("#help-tag-varia").css('display', (this.value == 'varia') ? 'block' : 'none');
  });
  // extra input velden voor stelling
  $("#stelling-toevoegen").change(function () {
    $("#stelling-info").toggle();
  });
});

$(document).ready(function(){
  // extra velden op basis van type verslag
  $("#interclubs-info").css('display', ($('#type-verslag').attr("value") == 'ni') ? 'block' : 'none');
  //$("#leeg-info").css('display', ($('#type-verslag').attr("value") == 'leeg') ? 'block' : 'none');
  $('#type-verslag').on('change', function () {
    $("#interclubs-info").css('display', (this.value == 'ni') ? 'block' : 'none');
    //$("#leeg-info").css('display', (this.value == 'leeg') ? 'block' : 'none');
  });
  // extra input velden voor stelling
  $("#stelling-toevoegen").change(function () {
    $("#stelling-info").toggle();
  });
});

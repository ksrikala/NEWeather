var multiselectEnable = {
	        maxHeight: 150,
	        numberDisplayed: 1,
	        enableFiltering: true,
	        enableCaseInsensitiveFiltering: true,
	        includeFilterClearBtn: false,
}
$(document).ready(function() {
	$('.selectpicker').selectpicker({
	  size: 5
	});
	 $('.datepicker').datepicker({
		format: 'mm/dd/yyyy',
		endDate: '+0d',
		autoclose: true
	 });
});   
$(document).on('click', '[name="environment"]' , function(){
    var val = $('[name="environment"]:checked').val();
    var ex={env:val}
    $.ajax({
        url: "/post1/",
        type: "POST", // or "get"
        headers: {'X-CSRFToken': '{{ csrf_token }}'},
        data: ex,
        dataType: 'json',
        success: function(data) {
          $('#hello').selectpicker('destroy');
          $('#services').selectpicker('destroy');
          var j_data = JSON.parse(data);
          var datalist = new Array();
          var datalist1 = new Array();
          $.each(j_data['reg'], function(index, val) {
            datalist.push("<option value = '" + val + "'>" + val + "</option>");
          });
          $.each(j_data['ser'], function(index, val1) {
            datalist1.push("<option value = '" + val1 + "'>" + val1 + "</option>");
          });
          $('#hello').html(datalist);
          $('#services').html(datalist1);
          $('#hello').selectpicker(multiselectEnable);
          $('#services').selectpicker(multiselectEnable);
          google_maps(val);
        }});
  
  }); 
  
$(document).ready(function() {
  $('#templatename').keyup(function() {

    var value = $(this).val();
    var ex={env:value}
    $.ajax({
      type: 'POST',
      url : '/tempcheck/',
      headers: {'X-CSRFToken': '{{ csrf_token }}'},
      data: ex,
      dataType: 'json',
      success:function(data)
      {
    	  alert("hi");
        if(data== 'ok')
        {
          $('#terror').show()
        }
        else
        {
          $('#terror').hide()
        }

      }

    });
});
});
  $(document).ready(function () {
    $('#form1').validate({
      errorClass: "my-error-class",
      validClass: "my-valid-class",
    rules: {
         services : { required: true},
         regions : { required : true}, 
         fromdate : { required: true },
         todate: { required: true },
         templatename : { required: true },
    },
    messages: {
         regions: "Select Regions",
         services: "Select Services", 
         fromdate: "Select From-Date",
         todate: "Select To-Date",
    },

  });

    $("#save").click(function(){
     $("#temp").show();
     $('#saveorrun').val(1);
});  

    $("#run1").click(function(){
    $("#validation").submit();

    });  
  
    });    
"use strict";!function(e){e(document).on("change","#id_status",function(a){"created"===e(this).val()?(e("#serial_number_box").hide(),e("#serial_number_box").data("values",e("#id_serial_numbers").val()),e("#id_serial_numbers").val(""),e("#id_serial_numbers").prop("disabled",!0)):(e("#id_serial_numbers").val(e("#serial_number_box").data("values")),e("#id_serial_numbers").prop("disabled",!1),e("#serial_number_box").show())}),e(document).on("change","#id_email",function(a){e.getJSON("/api/v1/users/",{email:e("#id_email").val()},function(a){1==a.count?(e("#id_phone_number_modified").val(a.results[0].phone_number),e("#id_first_name").val(a.results[0].first_name),e("#id_last_name").val(a.results[0].last_name),e("#id_phone_number_modified").prop("readonly",!0),e("#id_first_name").prop("readonly",!0),e("#id_last_name").prop("readonly",!0)):(e("#id_phone_number_modified").prop("readonly",!1),e("#id_first_name").prop("readonly",!1),e("#id_last_name").prop("readonly",!1))})})}(jQuery);
//# sourceMappingURL=order_create.js.map
$(document).ready(function(){

    $('#load-order-form').submit(function(e){
        e.preventDefault();  
        
        if($("#number").val() != ""){
            var post_url = $(this).attr("action"); 
            var request_method = $(this).attr("method");
            var form_data = $(this).serialize();
            $.ajax({
                url : post_url,
                type: request_method,
                data : form_data,
                success : function(response){
                    console.log(response);
                    $('#order-number-error').html('')

                    var obj = response;
                    var today = new Date();
                    var year = today.getFullYear(); 
                    var month = ((today.getMonth()+1) < 10 ? '0' : '') + today.getMonth(); 
                    var day = (today.getDate() < 10 ? '0' : '') + today.getDate(); 
                    var date = day + '-' + month +'-'+ year;
                    var hours = (today.getHours() < 10 ? '0' : '') + today.getHours(); 
                    var minutes = (today.getMinutes() < 10 ? '0' : '') + today.getMinutes(); 
                    var time = hours + ":" + minutes;
                    var dateTime = date+' '+time;

                    $('#id_owner').val(obj.detail.owner_id);
                    $('#id_owner').trigger('change');

                    $('#id_product').val(obj.detail.lines[0].product_id);
                    $('#id_product').trigger('change');

                    $('#id_quantity').val(obj.detail.quantity);
                    $('#id_email').val(obj.detail.email);
                    $("#id_phone_number_modified").intlTelInput("setNumber", obj.detail.phone_number);

                    $('#id_total_incl_tax').val(obj.detail.total_incl_tax);
                    
                    $('#id_currency').val(obj.detail.currency); 
                    $('#id_currency').select2().trigger('change');

                    $('#id_date_placed').val(dateTime);
                    $('#id_country').val(obj.detail.shipping_address.country); 
                    $('#id_country').select2().trigger('change');

                    $('#id_first_name').val(obj.detail.shipping_address.first_name);
                    $('#id_last_name').val(obj.detail.shipping_address.last_name);
                    $('#id_postcode').val(obj.detail.shipping_address.postcode);
                    $('#id_state').val(obj.detail.shipping_address.state);
                    $('#id_line1').val(obj.detail.shipping_address.line1);

                },
                error : function(error){
                    console.log(error);
                    $('#order-number-error').html("Invalid order number!");
                }
            });
        }
    
    });

});
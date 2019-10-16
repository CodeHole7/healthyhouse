$(document).ready(function(){
    
    $('.add_order_note').click(function(){
        var number = $(this).data('number');
        var uri = number+"/?note=";
        $('#add_note_form').attr('action', uri);
        $('#note_modal_form').modal('show');
    });

    $('.add_dosimeter_note').click(function(){
        var uuid = $(this).data('uuid');
        var uri = "/api/v1/dosimeters/add_dosimeter_note/";
        $('#add_note_form').attr('action', uri);
        $('#uuid').val(uuid);
        $('#note_modal_form').modal('show');
    });

    $('#add_note_form').submit(function(e){
        e.preventDefault();       
        $('#id_message').val(CKEDITOR.instances['id_message'].getData());
        var post_url = $(this).attr("action"); 
        var request_method = $(this).attr("method");
        var form_data = $(this).serialize();
        
        $.ajax({
            url : post_url,
            type: request_method,
            data : form_data,
            success : function(response){
                CKEDITOR.instances['id_message'].setData('');
                $('#note_modal_form').modal('hide');
            }
        });
    
    });
});
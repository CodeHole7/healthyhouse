$(document).ready(function(){
    
    add_dosimeter_note = function(e){
        var uuid = e.data('uuid');
        var note_type = $('#note_type').val();

        $.ajax({
          url : "/api/v1/dosimeters/get_dosimeter_note/",
          type: 'POST',
          data : {'uuid':uuid, 'note_type':note_type},
          success : function(response){
              ret = response;
              if(ret.success){
                CKEDITOR.instances['id_message'].setData(ret.message);
              }else{
                CKEDITOR.instances['id_message'].setData('');
              }

              var uri = "/api/v1/dosimeters/add_dosimeter_note/";
              $('#add_note_form').attr('action', uri);
              $('#uuid').val(uuid);
              $('#note_modal_form').modal('show');
          }
        });        
    }

    add_order_note = function(e){
        var number = e.data('number');
        var uri = number+"/?note=";
        $('#add_note_form').attr('action', uri);
        $('#note_modal_form').modal('show');
    }

    $('.add_order_note').click(function(){
        add_order_note($(this));
    });

    $('.add_dosimeter_note').click(function(){
        add_dosimeter_note($(this))
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
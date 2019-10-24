$(document).ready(function(){
    
    window.add_dosimeter_note = function(e){
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

    window.add_order_note = function(e){
      var number = e.data('number');
      var note_type = $('#note_type').val();
      
      $.ajax({
        url : "/api/v1/orders/get_order_note/",
        type: 'POST',
        data : {'number':number, 'note_type':note_type},
        success : function(response){
            ret = response;
            if(ret.success){
              CKEDITOR.instances['id_message'].setData(ret.message);
            }else{
              CKEDITOR.instances['id_message'].setData('');
            }

            var uri = "/api/v1/orders/add_order_note/";
            $('#add_note_form').attr('action', uri);
            $('#add_note_form #number').val(number);
            $('#note_modal_form').modal('show');
        }
      });    

    }

    window.enable_note = function(e){
      e.parent().parent().find(".add_dosimeter_note").prop('disabled', false);
    }
    
    window.disable_note = function(e){
      e.parent().parent().find(".add_dosimeter_note").prop('disabled', true);
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
    
    initWYSIWYG = function(el) {
      var r = /^<script[\s\S]*?>[\s\S]*?<\/script>/gi;
      $textareas = $(el)
        .find("textarea")
        .not(".no-widget-init textarea")
        .not(".no-widget-init");
      $textareas.each(function() {
        CKEDITOR.replace(this, {
          toolbar: "standard",
          width: "100%",
          basicEntities: false,
          disallowedContent: "script; *[on*]",
          on: {
            paste: function(evt) {
              var editor = evt.editor,
                data;
              try {
                data = evt.data.dataTransfer._.data.Text;
                if (r.test(data)) {
                  editor.setData("<p>scripts are not allowed</p>");
                }
              } catch (err) {
                console.warn(err);
              }
            }
          },
          filebrowserUploadUrl: "/ckeditor/upload/",
          filebrowserBrowseUrl: "/ckeditor/browse/"
        });
      });
    }

    initWYSIWYG(window.document);


});
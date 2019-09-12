var oscar = (function(o, $) {
  o.page = {
    instructionCreatePage: {
      conf: {
        base64Prefix: "data:image/png;base64,",
      },
      renderErrors: function(errors) {
        var errHtml =
          '<span class="error-block"><i class="icon-exclamation-sign"></i> {{$}}</span>';
        for (name in errors) {
          if (!errors.hasOwnProperty(name)) continue;

          $('[name="' + name + '"]')
            .parent()
            .append($(errHtml.replace("{{$}}", errors[name][0])));
        }
      },
      removeImage: function () {
        var btn = $(this);
        var id = btn.data('id');
        var url = o.page.instructionCreatePage.conf.url + id
        btn.prop('disabled', true);
        $.ajax({
          type: "delete",
          url: url,
          cache: false,
          success: function() {
            btn.closest('.js-image-item-row').remove();
            o.messages.clear();;
          },
          error: function(response) {
            btn.prop('disabled', true);
            o.messages.clear();
            var errorObj = JSON.parse(response.responseText);
            if (errorObj.detail) {
              o.messages.error(errorObj.detail);
              return;
            }
            o.messages.error("Something going wrong. Please, try again");
          },
        });
      },
      uploadImage: function(){
        const that = o.page.instructionCreatePage;
        that.conf.$submitUpload.prop('disabled', true);
        var fd = new FormData();
        var file = that.conf.$fileInput.get(0).files[0];
        fd.append('image', file, file.name);

        $.ajax({
            url: that.conf.url,
            type: 'POST',
            data: fd,
            contentType: false,
            processData: false,
            beforeSend: function (xhr) {
              $(".error-block").remove();
              xhr.setRequestHeader("X-CSRFToken", $('[name="csrfmiddlewaretoken"]').val());
            },
            success: function(response){
              var textTemplate = that.conf.template
                .replace(/{url}/g, response.image)
                .replace(/{id}/g, response.id)
              
              that.conf.$listContainer.append(textTemplate)
            },
            error: function (response) {
              var errorObj = JSON.parse(response.responseText);
              console.log(errorObj)
              that.renderErrors(errorObj);
            }
        })
        .always(function () {
          that.conf.$fileInput.val('');
          that.conf.$submitUpload.prop('disabled', true);
        })
      },
      init: function(opt) {
        var that = this;
        $.extend(that.conf, opt);
        that.conf.$listContainer = $(".js-images-list");
        that.conf.$fileInput = $('#id_image_upload');
        that.conf.$submitUpload = $('.js-image-upload');
        that.conf.template = $('#js-image-item-row-template').text();
        that.conf.$listContainer.on('click', '.js-image-item-remove', that.removeImage);
        that.conf.$fileInput.on('onload:image', function(e, data) {
          if(!!data.target.result) {
            that.conf.$submitUpload.prop('disabled', false)
          }
        });
        that.conf.$submitUpload.click(that.uploadImage);
      }
    }
  }

  return o;

})(oscar || {}, jQuery);

$(($) => {
    'use strict';
    ////////////////////////////////////////////////////////////
    ///    Subscribe form
    ////////////////////////////////////////////////////////////
    var $form = $('.subscribe-form');
    var $confirmBtn = $form.find('button');

    var validateForm = function(){
        var valid = true;
        var value;

        $form.find('.has-error')
            .removeClass('has-error');

        $form.find('.errorlist li').addClass('hidden');

        $form.find('input').not('[type="hidden"]').each(function() {
            value = $( this ).val();
            if(!value ) {
                $form.find('.blank').removeClass('hidden');
                valid = false;
            }

            if($( this ).is( '[type="email"]' ) && value) {
                if(!_utils.validateEmail( value )) {
                    $form.find('.invalid').removeClass('hidden');
                    valid = false;
                }
            }
        });

        return valid;
    };

    var sendRequest = function() {
        $.ajax({
            url: $form[0].action,
            method: $form[0].method,
            data: $form.serialize(),
            beforeSend: function() {
                $confirmBtn.prop('disabled', true);
            },
            error: function(data) {
                $confirmBtn.prop('disabled', false);
                _utils.renderMessages('warning', data.responseJSON.errors['email']);
            },
            success: function(data) {
                _utils.renderMessages('success', data.message);
                $form.find('input').not('[type="hidden"]').val('');
                setTimeout(function() {
                    $confirmBtn.prop('disabled', false);
                }, 5000);
            }
        });
    };


    $form[0].onsubmit = function (e) {
        e.preventDefault();
        var disabled = $confirmBtn.prop('disabled');
        if (!disabled) {
            $confirmBtn.blur();
            if (validateForm()) {
                sendRequest();
            }
        }
        return false;
    };
});

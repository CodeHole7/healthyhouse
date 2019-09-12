(($) => {
    'use strict';

    let $form = $('#contact-us-form');
    let $confirmBtn = $form.find('button[type="submit"]');
    let formValid = false;

    let requiredError = window._radonOptions.requiredError;
    let invalidEmailError = window._radonOptions.invalidEmailError;

    const validateForm = () => {
        let valid = true;
        let value;
        let field;

        $form.find('.has-error')
            .removeClass('has-error')
            .find('.errorlist, .error-block')
            .remove();

        $form.find('.nonfield')
            .remove();

        $form.find('input, textarea').not('[type="hidden"]').each(function() {
            value = $( this ).val();
            if(!value && $( this ).attr('required') ) {
                field = $( this ).parents('.form-group')
                    .addClass('has-error')
                    .append($(requiredError));

                valid = false;
            }

            if($( this ).is( `[type="email"]` ) && value) {
                if(!_utils.validateEmail( value )) {
                    $( this ).parents('.form-group')
                        .addClass('has-error')
                        .append($(invalidEmailError));
                    valid = false;
                }
            }
        });

        return valid;
    };

    const sendToZendesk = ($form, $confirmBtn, submit_to_server) => {
        let formSubmited = false;
        let data = {
            "request": {
                "requester": {
                    "name": $form.find('#id_name').val(),
                    "email": $form.find('#id_email').val(),
                    "local_id": window._radonOptions.locale_id
                },
                "subject": `Contact us web form | ${$form.find('#id_name').val()}`,
                "comment": {
                    "body": $form.find('#id_message').val()
                },
                "via": {
                    "channel": "web"
                }
            }
        };

        $.ajax({
            url: window._radonOptions.zendesk_request_api,
            type: 'POST',
            data: data,
            error: (data) => {
                $form.submit();
                formSubmited = true;
            },
            success: (data) => {
                _utils.renderMessages('success', window._radonOptions.success_send);

                if(submit_to_server) { return; }

                $form.find('input, textarea').not('[type="hidden"]').not('#g-recaptcha-response').val('');
                setTimeout(function() {
                    $confirmBtn.prop('disabled', false);
                }, 5000);

                formValid = false
            }
        })
        .always(() => {
            if(submit_to_server && !formSubmited) {
                $form.submit();
            }
        });
    };


    $form[0].onsubmit = function (e) {
        if(!grecaptcha.getResponse()) {
            e.preventDefault();
            return false
        }
        if(formValid) {
            return true;
        } else {
            e.preventDefault();
            var disabled = $confirmBtn.prop('disabled');
            if (!disabled) {
                $confirmBtn.blur();
                if (validateForm()) {
                    formValid = true;
                    sendToZendesk($form, $confirmBtn, $form.data('submit-to-server'));
                    $confirmBtn.prop('disabled', true);
                }
            }
            return false;
        }
    };

    autosize($form.find('textarea'));

})(jQuery);

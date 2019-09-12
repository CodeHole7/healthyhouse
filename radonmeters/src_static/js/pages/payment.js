(($) => {
    'use strict';

    let $form = $('#stripe_form');
    let $subscribe = $('#view_preview');

    let stripe = Stripe(window._radonOptions.stripe_pk);

    const errorhandler = function (event) {
        let displayError = $(`.${$(this._parent).attr('id')}-error`)[0];
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    }

    const style = {
        base: {
            color: '#426891',
            fontSize: '16px',
            lineHeight: '58px',
            fontSmoothing: 'antialiased',
            '::placeholder': {
                color: '#CAD3E1',
            },
        },
        invalid: {
            color: '#FF446F',
            ':focus': {
                color: '#FF446F',
            },
            '::placeholder': {
                color: '#FF446F',
            }
        },
    };

    let elenemts = stripe.elements();
    let cardNumber = elenemts.create('cardNumber', {
        style: style,
        hidePostalCode: true,
        placeholder: 'xxxx xxxx xxxx xxxx'
    });
    cardNumber.addEventListener('change', errorhandler.bind(cardNumber));
    let cardNumberField = cardNumber.mount('#cardNumber');
    //
    let cardExpiry = elenemts.create('cardExpiry', {
        style: style,
        hidePostalCode: true,
        placeholder: "MM / YYYY"
    });
    cardExpiry.addEventListener('change', errorhandler.bind(cardExpiry));
    let cardExpiryField = cardExpiry.mount('#cardExpiry');
    //
    let cardCVC = elenemts.create('cardCvc', {
        style: style,
        hidePostalCode: true,
        placeholder: 'CVV'
    });
    cardCVC.addEventListener('change', errorhandler.bind(cardCVC));
    let cardCVCField = cardCVC.mount('#cardCVC');
    //
    let postalCode = elenemts.create('postalCode', {
        style: style,
        hidePostalCode: true,
        placeholder: 'Enter code'
    });
    postalCode.addEventListener('change', errorhandler.bind(postalCode));
    postalCode.on('ready', function () {
         $('.card-dimmer').hide();
    });
    let postalCodeField = postalCode.mount('#postalCode');

    let createToken = function () {
        stripe.createToken(cardNumber).then(function (result) {
            if (result.error) {
                $subscribe.prop('disabled', false);
                $('.card-dimmer').hide();
                // Inform the user if there was an error
                let errorElement = $('.payment-errors')[0];
                errorElement.textContent = result.error.message;
            } else {

                // Send the token to your server
                stripeTokenHandler(result.token);
            }
        });
    };

    $subscribe.click(function () {
        $form.submit();
    });



    $form.on('submit', function (event) {
        event.preventDefault();
        createToken();
        $subscribe.prop('disabled', true);
        $('.card-dimmer').show();
    });

     function stripeTokenHandler(obj) {
        $('#id_card_data').val(JSON.stringify(obj));
        // $('#id_card_id').val(obj['card']['id']);
        // $('#id_card_token').val(obj['id']);
        $('#payout_form').submit();
    }

})(jQuery);

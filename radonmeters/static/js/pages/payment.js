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

    /**
        @author: alex m
        @created: 2019.9.5
        @desc: upgrade stripe
    */

    let createToken = function () {
        stripe.createPaymentMethod(
          'card',
          cardNumber
        ).then(function(result) {
          if (result.error) {
            // Show error in payment form
            $subscribe.prop('disabled', false);
            $('.card-dimmer').hide();
            // Inform the user if there was an error
            let errorElement = $('.payment-errors')[0];
            errorElement.textContent = result.error.message;
          } else {
                // Send the token to your server
                stripeTokenHandler('payment_method', result.paymentMethod);
          }
        });
    };


    // old version
    // let createToken = function () {
    //     stripe.createToken(cardNumber).then(function (result) {
    //         if (result.error) {
    //             $subscribe.prop('disabled', false);
    //             $('.card-dimmer').hide();
    //             // Inform the user if there was an error
    //             let errorElement = $('.payment-errors')[0];
    //             errorElement.textContent = result.error.message;
    //         } else {

    //             // Send the token to your server
    //             stripeTokenHandler(result.token);
    //         }
    //     });
    // };


    /**
        @author: alex m
        @created: 2019.9.5
        @desc: upgrade stripe
    */
    $subscribe.click(function () {
        $form.submit();
    });


    /**
        @author: alex m
        @created: 2019.9.5
        @desc: upgrade stripe
    */
    $form.on('submit', function (event) {
        event.preventDefault();

        createToken();
        $subscribe.prop('disabled', true);
        $('.card-dimmer').show();
    });
    
    /**
        @author: alex m
        @created: 2019.9.5
        @desc: upgrade stripe
    */
    function stripeTokenHandler(key, obj) {

        var array = [];

        $('#id_' + key).val(JSON.stringify(obj));

        $('#'+key+"_form").submit();
    }

})(jQuery);

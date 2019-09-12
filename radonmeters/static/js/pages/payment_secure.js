/**
    This file is created by alex m
*/
(($) => {
    'use strict';

    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

    let $place_order = $('#place-order');

    let $form = $('#place_order_form');
    let $secure_form = $('#secure_form');

    let stripe = Stripe(window._radonOptions.stripe_pk);

    $place_order.click(function () {
        $form.submit();
    });



    $form.on('submit', function (event) {
        event.preventDefault();
        submit_form();
    });


    /**
        @author: alex m
        @created: 2019.9.5
        @desc: upgrade stripe
    */
    function submit_form() {
        var array = [];


        array = $form.serializeArray();
        var jsondata = {};
        
        for (var i = array.length - 1; i >= 0; i--) {
            jsondata[array[i].name] = array[i].value;
        }

        $('body').prepend('<div id="loader" style="left:0;top:0;position:fixed;margin:0;padding:0;width:100%;height:100%; background:rgba(0,0,0,0.9);z-index:1000"><div class="loader" style="position: absolute;left: 50%;top: 50%;transform: translate(50%, 50%);"></div></div>')
        $.post($form.attr("action"), jsondata,
            function(result) {
                // Handle server response (see Step 3)
                handleServerResponse(result);
            }
        );
    }

    /**
        @author: alex m
        @created: 2019.9.5
        @desc: upgrade stripe
    */
    function handleServerResponse(response) {
        console.log('response', response);
        if (response.error) {
            alert(response.error.message);
            // Show error from server on payment form
        } else if (response.requires_action) {
            // Use Stripe.js to handle required card action
            return handleAction(response);
        } else if(response.success_url) {
            // Show success message
            location.href = response.success_url;
        }else {
            alert('unknow error');
        }

        $('#loader').remove();

    }

    /**
        @author: alex m
        @created: 2019.9.5
        @desc: upgrade stripe
    */

    function handleAction(response) {
      stripe.handleCardAction(
        response.payment_intent_client_secret
      ).then(function(result) {
        
        if (result.error) {            
            // Show error in payment form
           $.post($form.attr("action"),{ error: true, action:'place_order'},
                function(data) {
                    alert(result.error.message);
                    $('#loader').remove();
                }
            );
        } else {

            
           $.post($form.attr("action"),{payment_intent_id: result.paymentIntent.id, action:'place_order'},
                function(result) {
                    // Handle server response (see Step 3)
                    if (result.error) {
                        alert(result.error.message);
                        $('#loader').remove();
                        // Show error from server on payment form
                    } else if(result.success_url) {
                        // Show success message
                        
                        location.href = result.success_url;
                    }else {
                        alert(result.error.message);
                        $('#loader').remove();
                    }
                }
            );
        }
      });
    }



})(jQuery);

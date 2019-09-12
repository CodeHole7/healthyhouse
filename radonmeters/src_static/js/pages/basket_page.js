(($) => {
    'use strict';

    let basketUrl = window._radonOptions.basketURL;
    let $messagesWrapper = $('#messages');
    let $basketContent = $('.basket-page-content');

    let disallowToChange = false;
    let disallowToUpdate = false;

    let updateBasket = () => {
        if(disallowToUpdate) { return; }
        disallowToChange = true;
        $basketContent.find('.dimmer').show();
        let $form = $basketContent.find('form');
        $basketContent.find('#procced-basket').addClass('disabled');
        $.ajax({
            type: 'POST',
            url: $form.attr('action'),
            data: $form.serialize(),
            success: (data) => {
                $basketContent.html(data.content_html);
                for (let level in data.messages) {
                    for (let i=0; i<data.messages[level].length; i++) {
                        _utils.renderMessages(level, data.messages[level][i]);
                    }
                }
                setQuantity();
                bindCoupon();
                disallowToChange = false;
            },
            error: (data) => {
                console.warn('error', data);
                disallowToChange = true;
            },
            always: () => {
                $basketContent.find('#procced-basket').removeClass('disabled');
            }
        });
    };


    $basketContent.on('click', '.remove-item', function (e) {
        e.preventDefault();

        var formID = $(this).data('id');
        var inputID = '#id_form-' + formID + '-DELETE';
        $(inputID).attr('checked', 'checked');

        updateBasket($(this).closest('form'));
    });

    ////////////////////////////////////////////////
    /// quantity input
    ////////////////////////////////////////////////
    let updateFormDebounce = _utils.debounce(updateBasket, 400);;
    function setQuantity() {
        $('.quantity').each(function (ind, elem) {
            let $quantityWrapper = $(this);
            let $quantityfield = $quantityWrapper.find('input');
            let $incr = $quantityWrapper.find('.quantity-incr');
            let $decr = $quantityWrapper.find('.quantity-decr');
            let max = +$quantityfield.attr('max') ? +$quantityfield.attr('max') : 10000;
            let min = +$quantityfield.attr('min');
            let currentVal = +$quantityfield.val();
            let getValueInRange = (val) => {
                if(val > max) {
                    return parseFloat(max);
                } else if(val < min) {
                    return parseFloat(min);
                } else {
                    return val;
                }
            };

            $quantityfield.on('keypress input cut paste', function () {
                let number = $(this).val();

                if(number !== 0 && !number) {
                    disallowToUpdate = true;
                    $basketContent.find('#procced-basket').addClass('disabled');
                    return;
                } else {
                    disallowToUpdate = false;
                    $basketContent.find('#procced-basket').removeClass('disabled');
                }

                if(number > max) {
                    number = `${max}`;
                }
                if(number < min) {
                    number = `${min}`;
                }
                let value = (number.split('.'));
                if (value[1]){
                    number = parseFloat(number[0]).toFixed(0);
                }
                currentVal = +number;
                $(this).val( number );

               updateFormDebounce();
            });

            $incr.on('click', function (e) {
                e.preventDefault();
                if(disallowToChange) { return; }
                if(currentVal >= max) { return; }
                $quantityfield.val(currentVal + 1);
                currentVal = currentVal + 1;
                updateFormDebounce();
            });
            $decr.on('click', function (e) {
                e.preventDefault();
                if(disallowToChange) { return; }
                if(currentVal == min) { return; }
                $quantityfield.val(currentVal - 1);
                currentVal = currentVal - 1;
                updateFormDebounce();

            });
        });
    }

    setQuantity();



    ////////////////////////////////////////////////
    /// coupon
    ////////////////////////////////////////////////

    const requiredError = window._radonOptions.requiredError;
    const invalidEmailError = window._radonOptions.invalidEmailError;


    function bindCoupon() {
        let $form = $('#voucher_form');
        let $confirmBtn = $form.find('button');
        let formValid = false;
        $('#voucher_form_link').click(function (e) {
            e.preventDefault();
            $(this).hide();
            $('#voucher_form_container').show();
        });

        $('#voucher_form_cancel').click(function (e) {
            e.preventDefault();
            $('#voucher_form_container').hide();
            $('#voucher_form_link').show();
        });

        $form[0].onsubmit = function (e) {
            if(formValid) {
                return true;
            } else {
                e.preventDefault();
                var disabled = $confirmBtn.prop('disabled');
                if (!disabled) {
                    $confirmBtn.blur();
                    if (_utils.validateForm($form, requiredError, invalidEmailError)) {
                        formValid = true;
                        $form.submit();
                        $confirmBtn.prop('disabled', true);
                    }
                }
                return false;
            }
        };
    }

    bindCoupon();


})(jQuery);

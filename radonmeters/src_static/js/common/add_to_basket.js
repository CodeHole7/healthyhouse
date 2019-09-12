(($) => {
    'use strict';
    let $addToCart = $('.cart-link');

    if(!$addToCart.length){ return; }

    $addToCart.click(function (e) {
        $(this).addClass('disabled');
        e.preventDefault();
        let alert;
        $.ajax({
            type: 'POST',
            url: $(this).attr('href'),
            data: {
                csrfmiddlewaretoken: $(this).find('input').val(),
                quantity: +$(this).data('quantity')
            },
            success: (data) => {
                alert = $(data).find('#messages .alert');
                _utils.renderMessages('success', alert);
                $('.basket-mini strong').text($(data).find('.basket-mini strong').first().text());
            }
        }).always(() => {
            $(this).removeClass('disabled');
        });
    });
})(jQuery);

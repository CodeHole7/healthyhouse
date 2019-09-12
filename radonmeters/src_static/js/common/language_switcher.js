(($) => {
    'use strict';

    const $container = $('.language-link');
    const csrf = $container.find('[name="csrfmiddlewaretoken"]').val();
    const next = $container.find('[name="next"]').val();


    $container.find('[data-name="language"]').on('click', function (e) {
        e.preventDefault();

        if($(this).parent().is('.active')) {
            return;
        }

        $.ajax($container.data('url'), {
            type: 'POST',
            data: {
                csrfmiddlewaretoken: csrf,
                next: next,
                language: $(this).data('lang-code')
            },
            success: (data) => {
                location.reload();
            }
        });
    });
})(jQuery)

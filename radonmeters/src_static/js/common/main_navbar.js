(($) => {
    'use strict';
    let $wrapper = $('.navbar-search-wrapper');
    $('.search-wrapper-toggle').click(function (e) {
        e.preventDefault();
        $wrapper.toggleClass('vis');
        if($wrapper.hasClass('vis')) {
            $wrapper.find('input').focus();
        } else {
            $wrapper.find('input').blur();
        }
    });

})(jQuery);

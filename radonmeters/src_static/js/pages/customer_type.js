(($) => {
    'use strict';
    let tabs = $('.customer-type .section-tab');

    tabs.on('click', function (e) {
        e.preventDefault();
        let activeTab;
        tabs.removeClass('active');
        $('.login_form, .continue_form').removeClass('show');
        activeTab = $(this);
        activeTab.addClass('active');
        $(activeTab.attr('href')).addClass('show');
    });
})(jQuery);

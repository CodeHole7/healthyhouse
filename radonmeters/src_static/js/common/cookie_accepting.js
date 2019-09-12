(($) => {
    'use strict';

    const expDate = 10;

    window.cookieconsent.initialise({
        container: document.getElementById("app"),
        palette: {
            popup: { background: "#F7F9FC" },
            button: { background: "#83CEFF", text: '#FFFFFF' },
        },
        /*revokable:true,*/
        onStatusChange: function(status) {
            console.log(this.hasConsented() ?
                'enable cookies' : 'disable cookies');
        },
        law: {
            regionalLaw: true,
        },
        status: {
            deny: 'deny',
            allow: 'allow',
            dismiss: 'dismiss'
        },
        cookie: {
            name: 'cookieOn'
        },
        static: true,
        expiryDays: expDate,
        location: false,
        theme: 'block',
        position: "top",
        type: "opt-in",
        content: {
            header: 'Cookies used on the website!',
            message: window._cookie_msg,
            dismiss: 'ok',
            allow: 'Ok'
        },
        elements: {
            message: '<span id="cookieconsent:desc" class="cc-message">{{message}}</span>',
            messagelink: '<span id="cookieconsent:desc" class="cc-message">{{message}}</span>',
            dismiss: '',
            allow: '<a aria-label="allow cookies" tabindex="0" class="cc-btn cc-allow btn btn-primary btn-sm">{{allow}}</a>',
            link: ''
        }
    });

    if(window.cookieconsent.utils.getCookie('cookieOn') !== 'allow') {
        $('a').on('click', (e) => {
            window.cookieconsent.utils.setCookie('cookieOn', 'allow', expDate);
        });
    }
})(jQuery);

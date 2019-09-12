;(($, g) => {
    'use strict';



    $.fn._wait = function (time) {
        let timout;
        let that = $(this);
        return new Promise(function(resolve, reject) {
            timout = setTimeout(function() {
                resolve(that);
                clearTimeout(timout);
                timout = null;
            }, time);
        });
    };

    $.fn._measureScrollBarWidth = (function () {
        const $body = $('body');

        return function () {
            let scrollDiv = document.createElement('div');
            scrollDiv.className = 'modal-scrollbar-measure';
            $body[0].append(scrollDiv);
            let scrollbarWidth = scrollDiv.offsetWidth - scrollDiv.clientWidth;
            $body[0].removeChild(scrollDiv);
            return scrollbarWidth;
        }
    })();

    $.Rm_popup = function Rm_popup(mainElement, options) {
        var o = {
            "popup":".popup-dialog",
            "close_btn":".close-popup",
            "afterClose":function(){},
            "beforeOpen": function() {},
            "beforeClose": function () {},
            "afterOpen": function () {}
        };

        var plugin = this;

        plugin.settings = {};

        var elem = $(mainElement);

        //
        // private methods
        //
        const setPaddingToBody = (() => {
            let paddingRight = 0;
            return ($holder, clear) => {
                paddingRight = (!clear) ? $holder._measureScrollBarWidth() + 'px' : 0;
                $('body').addClass('modal-open').css('paddingRight', paddingRight);
            }
        })();

        const close_popup = () => {
            let $holder = elem;

            $holder.trigger( 'close:rm_modal' );
            $holder.css('overflowY', 'hidden');
            $holder
                .find('.popup-dialog')
                .removeClass('show-dialog')
                ._wait(500)
                .then($elem => $elem.parents($holder).removeClass('animated_in')._wait(305))
                .then($elem => $elem.removeClass('show_popup_holder'))
                .then(() => {
                    $holder.trigger('closed:rm_modal');
                    $holder.attr('aria-hidden', 'true');
                    $holder.attr('aria-hidden', 'false');
                    plugin.settings.afterClose.apply($holder,[$holder]);
                    setPaddingToBody($holder, true);
                    $('body').removeClass('modal-open');

                    return $holder;
                });
        };

        const open_popup = () => {
            let $holder = elem;
            $holder.trigger( 'open:rm_modal' );
            plugin.settings.beforeOpen.apply($holder, [$holder]);
            setPaddingToBody($holder);
            $holder.css('overflowY', 'hidden');
            $holder
                .addClass('show_popup_holder')
                ._wait(50)
                .then($elem => $elem.addClass('animated_in')._wait(305))
                .then($elem => $elem.find('.popup-dialog').addClass('show-dialog')._wait(500))
                .then(() => {
                    $holder.trigger( 'opened:rm_modal' );
                    $holder.attr('aria-hidden', 'false');
                    $holder.css('overflowY', 'auto');
                    plugin.settings.afterOpen.apply($holder, [$holder]);
                    return $holder;
                });
        };


        plugin.init = function init() {
            plugin.settings = $.extend({}, o, options);

            var popup_holder = elem,
            popup = popup_holder.find(o.popup),
            close = popup.find(o.close_btn);

            popup_holder.click(function(e){
                if(!$(e.target).is(popup_holder)) { return; }
                e.stopPropagation();
                close_popup();
            });

            close.click(function(e){
                close_popup();
                e.preventDefault();
            });

            $('body').keydown(function(e){
                if(e.keyCode=='27'){
                    close_popup();
                }
            });
        };

        //
        // public methods
        //
        plugin.hide = () => close_popup();

        plugin.show = () => open_popup();

        plugin.init();
    };

    $.fn.rm_popup = function rm_popup(options) {
        return this.each(function() {
            if (undefined === $(this).data('rm_popup')) {
                var plugin = new $.Rm_popup(this, options);
                $(this).data('rm_popup', plugin);
            }
        });
    };

})(jQuery, window);



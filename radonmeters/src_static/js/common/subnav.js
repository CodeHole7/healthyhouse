(($) => {
    'use strict';
    // duration of scroll animation
    const scrollDuration = 300;
    // paddles
    let $leftPaddle = $('.left-paddle');
    let $rightPaddle = $('.right-paddle');
    // get items dimensions
    let itemsLength = $('.sub-nav-item').length;
    let itemSize = $('.sub-nav-item').outerWidth(true);
    // get some relevant size for the paddle triggering point
    const paddleMargin = 20;

    const offset = 150;

    // get wrapper width
    let getMenuWrapperSize = () => $('.sub-nav-inner-wrapper').outerWidth();

    let menuWrapperSize = getMenuWrapperSize();
    // the wrapper is responsive
    $(window).on('resize', function() {
        menuWrapperSize = getMenuWrapperSize();
    });
    // size of the visible part of the menu is equal as the wrapper size
    let menuVisibleSize = menuWrapperSize;

    // get total width of all menu items
    let getMenuSize = () => itemsLength * itemSize;

    let menuSize = getMenuSize();
    // get how much of menu is invisible
    let menuInvisibleSize = menuSize - menuWrapperSize;

    // get how much have we scrolled to the left
    let getMenuPosition = () => $('.sub-nav-list').scrollLeft();

    if(!itemsLength) { return; }

    const delay = 200;
    $('.sub-nav-item a').each(function ( inx, item ) {
        $(item).css('transitionDelay', delay * (inx + 0.3) / 1000 + 's').addClass('item-show');

    });

    let maxAnimationTime = delay * (($('.sub-nav-item a').length - 1) + 0.5) / 1000;
    let TO = setTimeout(function() {
        $('.sub-nav-item a').css('transitionDelay', 0 + 's');
        clearTimeout(TO);
        TO = null;
    }, maxAnimationTime);

    // finally, what happens when we are actually scrolling the menu
    $('.sub-nav-list').on('scroll', function() {

        // get how much of menu is invisible
        menuInvisibleSize = menuSize - menuWrapperSize;
        // get how much have we scrolled so far
        let menuPosition = getMenuPosition();

        let menuEndOffset = menuInvisibleSize - paddleMargin;

        // show & hide the paddles
        // depending on scroll position
        if (menuPosition <= paddleMargin) {
            $leftPaddle.addClass('hidden');
            $rightPaddle.removeClass('hidden');
        } else if (menuPosition < menuEndOffset) {
            // show both paddles in the middle
            $leftPaddle.removeClass('hidden');
            $rightPaddle.removeClass('hidden');
        } else if (menuPosition >= menuEndOffset) {
            $leftPaddle.removeClass('hidden');
            $rightPaddle.addClass('hidden');
        }
    });

    if(menuWrapperSize < menuSize) {
        $rightPaddle.removeClass('hidden');
    }

    $(window).resize(function () {
        if(menuWrapperSize < menuSize) {
            $rightPaddle.removeClass('hidden');
        } else {
            $rightPaddle.addClass('hidden');
        }
    });

    // scroll to left
    $rightPaddle.on('click', function() {
        let menuPos = getMenuPosition();
        let shift = menuPos + offset;
        $('.sub-nav-list').animate( { scrollLeft: shift }, scrollDuration);
    });

    // scroll to right
    $leftPaddle.on('click', function() {
        let menuPos = getMenuPosition();
        let shift = menuPos - offset;
        $('.sub-nav-list').animate( { scrollLeft: shift }, scrollDuration);
    });

     ////////////////////////////////////////////////////////////
    ///    Scrolling
    ////////////////////////////////////////////////////////////
    const DELAY = 0,
          DURATION = 300,
          POSTFIX = '_s';
    if(window.location.hash){
        let section = $(window.location.hash + POSTFIX);
        if(!section.length) { return; }
        $('html, body').animate({
            scrollTop: section.offset().top
        }, DURATION);
    }

    $('.sub-nav-item a').on('click', function (e) {
        e.preventDefault();
        window.location.hash = $(this).attr('href').substr(1);
        let section = $(window.location.hash + POSTFIX);
        if(!section.length) { return; }
        $('html, body').delay( DELAY ).animate({
            scrollTop: section.offset().top
        }, DURATION);
    });
})(jQuery);


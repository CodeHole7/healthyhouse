(($) => {
    'use strict';
    let $slider = $('.slider');
    let urls = [];

    if(!$slider.length) { return; }

    $slider.find('.slider-item').each(function (indx, elem) {
        urls.push($(elem).data('url'));
    });

    $slider.slick({
        infinite: true,
        arrows: true,
        autoplay: true,
        autoplaySpeed: 10000,
        focusOnSelect: false,
        pauseOnFocus: false,
        pauseOnHover:false,
        dots: true,
        appendDots: '.slick-dots-custom',
        dotsClass: 'slick-dots-inner'
    });
    let $linkBuyNow = $('.btn-shop-now');
    $linkBuyNow.attr('href', urls[0]);
    $slider.on('afterChange', function(event, slick, currentSlide){
        $linkBuyNow.attr('href', urls[currentSlide]);
    });

})(jQuery);

(($, global) => {
    'use strict';

    let $slider = $('.thumbnails-slider');
    let $preview = $('.image-view');

    const options = {
        zoomPosition: 'inside',
        autoInside: true,
        zoomSizeMode: 'zoom',
        zoomOffsetX: 0,
        zoomMatchSize: true
    };
    $preview.CloudZoom(options);

    $slider.on('click', '.thumbnail', function () {
        $slider.find('.thumbnail').removeClass('selected');
        $preview.data('CloudZoom').destroy();
        let src = $(this).addClass('selected').data('original');
        let original = $(this).data('cloudzoom');
        $preview.attr('src', src);
        $preview.attr('data-cloudzoom', original);
        $preview.CloudZoom(options);
    });
    let length = $slider.find('.thumbnail').length;
    $slider.slick({
        infinite: false,
        slidesToShow: length > 4 ? 4 : length,
        slidesToScroll: 1,
        arrows: length > 4 ? true : false,
        autoplay: false,
        focusOnSelect: true,
        vertical: true,
        verticalSwiping: true,
        prevArrow: $('.slick-prev'),
        nextArrow: $('.slick-next')
    });

    ////////////////////////////////////////////////
    /// quantity input
    ////////////////////////////////////////////////
    let $quantityWrapper = $('.quantity');
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
            return val
        }
    };
    $quantityfield.on('keypress input cut paste', function () {
        let number = $(this).val();

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
    });

    $incr.on('click', function (e) {
        e.preventDefault();
        if(currentVal >= max) { return; }
        $quantityfield.val(currentVal + 1);
        currentVal = currentVal + 1;
    });
    $decr.on('click', function (e) {
        e.preventDefault();
        if(currentVal == min) { return; }
        $quantityfield.val(currentVal - 1);
        currentVal = currentVal - 1;
    });

    ////////////////////////////////////////////////
    /// product details tab
    ////////////////////////////////////////////////
    const $tabs = $('.sub-section-tab');
    const DELAY = 0,
          DURATION = 300;
    const $contentWrapper = $('.additional-info-wrapper');
    let videoType;

    (() => {
        let src = $('#featured-video-frame').attr('src');

        if(!src) { return; }
        if(src.indexOf('vimeo') > -1) {
            videoType = 'vimeo';
        }

        if(src.indexOf('youtube') > -1) {
            videoType = 'youtube';
        }
    })();


    const setHeight = (event, $elem) => {
        let contentBlock = $elem || $('.content-block.active');
        $contentWrapper.css("minHeight", contentBlock.outerHeight(true));
    };

    setHeight(null);

    $(window).resize(setHeight);

    $tabs.on('click', function (e) {
        e.preventDefault();

        if($(this).hasClass('active')) { return; }

        $tabs.removeClass('active');
        $(this).addClass('active');
        $('.content-block.active').removeClass('active');
        let contentBlock = $($(this).data('content'));
        contentBlock.addClass('active');
        setHeight(null, contentBlock);
        stopPlayer(videoType);
    });

    $('.important-info').on('click', function (e) {
        e.preventDefault();
        $('.content-block.active').removeClass('active');
        let contentBlock = $($(this).data('content')).addClass('active');
        $tabs.removeClass('active');
        $tabs.filter(`[data-content="${$(this).data('content')}"]`).addClass('active');
        setHeight(null,contentBlock);

        stopPlayer(videoType);
        $('html, body').delay( DELAY ).animate({
            scrollTop: contentBlock.offset().top
        }, DURATION);
    });



    global.framePlayer = null;
    const apiUrls = {
        'youtube': "https://www.youtube.com/iframe_api",
        'vimeo': "https://player.vimeo.com/api/player.js"
    };

    function onloadFrameScript(videoType) {
        if(videoType === 'vimeo') {
            global.framePlayer = new global.Vimeo.Player($('#featured-video-frame')[0]);
        }

        if(videoType === 'youtube') {
            global.onYouTubeIframeAPIReady = function() {
                global.framePlayer = new global.YT.Player('featured-video-frame');
            };
        }
    }

    function stopPlayer(type) {
        if (global.framePlayer && type === 'youtube') {
            global.framePlayer.pauseVideo();
        } else if(global.framePlayer && type === 'vimeo') {
            global.framePlayer.pause().catch(function(error) {
                console.warn(error.name);
            });
        }
    }

    if(videoType) {
        // 2. This code loads the IFrame Player API code asynchronously.
        let tag = document.createElement('script');

        tag.src = apiUrls[videoType];
        let firstScriptTag = document.getElementById('forVideoApi');
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

        tag.onload = onloadFrameScript.bind(this, videoType);
    }
})(jQuery, window);

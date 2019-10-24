$(document).ready(function(){

    var n = $(".language-link"),
        t = n.find('[name="csrfmiddlewaretoken"]').val(),
        o = n.find('[name="next"]').val();
    n.find('[data-name="language"]').on("click", function(i) {
        i.preventDefault(), $(this).parent().is(".active") || $.ajax(n.data("url"), {
            type: "POST",
            data: {
                csrfmiddlewaretoken: t,
                next: o,
                language: $(this).data("lang-code")
            },
            success: function(e) {
                location.reload()
            }
        })
    });

    
    $('.re-lang a').each(function(){

        $(this).on("click",function(){
            
            $('#re_language_selector li.active').removeClass('active');
            $('#re-lang-name').html($(this).html());
            $(this).parent().addClass('active');
            $.cookie("re-lang-code", $(this).data('lang-code'), {path:'/'});
        });
    });

    function load_report_lang(){
        var report_lang_code = $.cookie("re-lang-code");

        if(report_lang_code){

            $('.re-lang a').each(function(){
                if(report_lang_code == $(this).data('lang-code')){
                    $('#re-lang-name').html($(this).html());
                    $(this).parent().addClass('active');
                }
            })
        }else{
            var display_lang = $('#language_selector li.active a');

            $('.re-lang a').each(function(){
                if(display_lang.data('lang-code') == $(this).data('lang-code')){
                    $('#re-lang-name').html($(this).html());
                    $(this).parent().addClass('active');
                }
            })
            
            $.cookie("re-lang-code", display_lang.data('lang-code'), {path:'/'});
        }
    }
   
    load_report_lang();
});
"use strict";!function(t){var s=t(".cart-link");s.length&&s.click(function(s){var a=this;t(this).addClass("disabled"),s.preventDefault();var e=void 0;t.ajax({type:"POST",url:t(this).attr("href"),data:{csrfmiddlewaretoken:t(this).find("input").val(),quantity:+t(this).data("quantity")},success:function(s){e=t(s).find("#messages .alert"),_utils.renderMessages("success",e),t(".basket-mini strong").text(t(s).find(".basket-mini strong").first().text())}}).always(function(){t(a).removeClass("disabled")})})}(jQuery);
//# sourceMappingURL=add_to_basket.js.map

"use strict";!function(e){window.cookieconsent.initialise({container:document.getElementById("app"),palette:{popup:{background:"#F7F9FC"},button:{background:"#83CEFF",text:"#FFFFFF"}},onStatusChange:function(e){},law:{regionalLaw:!0},status:{deny:"deny",allow:"allow",dismiss:"dismiss"},cookie:{name:"cookieOn"},static:!0,expiryDays:10,location:!1,theme:"block",position:"top",type:"opt-in",content:{header:"Cookies used on the website!",message:window._cookie_msg,dismiss:"ok",allow:"Ok"},elements:{message:'<span id="cookieconsent:desc" class="cc-message">{{message}}</span>',messagelink:'<span id="cookieconsent:desc" class="cc-message">{{message}}</span>',dismiss:"",allow:'<a aria-label="allow cookies" tabindex="0" class="cc-btn cc-allow btn btn-primary btn-sm">{{allow}}</a>',link:""}}),"allow"!==window.cookieconsent.utils.getCookie("cookieOn")&&e("a").on("click",function(e){window.cookieconsent.utils.setCookie("cookieOn","allow",10)})}(jQuery);
//# sourceMappingURL=cookie_accepting.js.map

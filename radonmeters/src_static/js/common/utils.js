(function($) {
  "use strict";

  var _utils = (window._utils = (function() {
    var utilsObj = {};

    utilsObj.ajaxRequest = function(url, method, formData, props) {
      if (!url || !method) {
        console.warn("put at least 2 params 1:url, 2:method, [3:formData]");

        return;
      }

      return new Promise(function(resolve, reject) {
        var config = {
          method: method,
          data: JSON.stringify(formData),
          url: url,
          dataType: "json",
          contentType: "application/json; charset=utf-8",
          success: resolve,
          error: reject
        };

        if (props)
          $.each(props, function(key, val) {
            config[key] = val;
          });

        $.ajax(config);
      });
    };

    utilsObj.detectMobile = function() {
      var check = false;

      (function(a) {
        if (
          /(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk/i.test(
            a
          ) ||
          /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(
            a.substr(0, 4)
          )
        ) {
          check = true;
        }
      })(navigator.userAgent || navigator.vendor || window.opera);

      return check;
    };

    utilsObj.unique = function(array) {
      var ArrayUnique = array.filter(function(item, idx) {
        return array.indexOf(item) === idx;
      });

      return ArrayUnique;
    };

    utilsObj.uniqueByKey = function(array, key) {
      var used = {};
      var ArrayUnique = array.filter(function(obj) {
        return obj[key] in used ? 0 : (used[obj[key]] = 1);
      });

      return ArrayUnique;
    };

    utilsObj.isArray = function(array) {
      if (Object.prototype.toString.call(array) === "[object Array]") {
        return true;
      }
      return;
    };

    utilsObj.isNumber = n => !isNaN(parseFloat(n)) && isFinite(n);

    utilsObj.isFunction = function(obj) {
      return (
        !!obj && Object.prototype.toString.call(obj) === "[object Function]"
      );
    };

    utilsObj.scrollTo = function($elem, duration) {
      var durat = duration ? duration : 200,
        fixedHeaderHeight = $(window).width() < 767 ? 0 : 73;
      var header = $elem;
      $("html, body").animate(
        {
          scrollTop: header.offset().top - fixedHeaderHeight
        },
        durat
      );
    };

    utilsObj.debounce = function(fn, timeout, invokeAsap, ctx) {
      if (arguments.length == 3 && typeof invokeAsap != "boolean") {
        ctx = invokeAsap;
        invokeAsap = false;
      }

      let timer;
      return function() {
        const args = arguments;
        ctx = ctx || this;

        invokeAsap && !timer && fn.apply(ctx, args);

        clearTimeout(timer);

        timer = setTimeout(() => {
          invokeAsap || fn.apply(ctx, args);
          timer = null;
        }, timeout);
      };
    };

    utilsObj.renderMessages = function(level, message) {
      let messageHTML;

      if (!level) {
        $("#messages").empty();
        return;
      }

      if (message instanceof jQuery) {
        messageHTML = message;
      } else {
        messageHTML = $(`<div class="alert alert-safe alert-noicon alert-${level} fade">
                    <a class="rm-icon-cross close" data-dismiss="alert" href="#"></a>
                    <div class="alertinner ">
                        ${message}
                    </div>
                </div>`);
      }

      $("#messages")
        .empty()
        .append(messageHTML);

      let time_out = setTimeout(function() {
        messageHTML.each(function(inx, item) {
          $(item)
            .delay(200 * (inx + 2))
            .addClass("in");
        });

        clearTimeout(time_out);
        time_out = null;
      }, 200);
    };

    utilsObj.validateEmail = mail => {
      const reg = /[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/;
      return reg.test(mail);
    };

    utilsObj.validatePhone = phone => {
      const plus = /^\+/;
      const reg = /^\+?[0-9]+$/;
      return reg.test(phone) && phone.replace(plus, "").length < 15;
    };

    utilsObj.validateForm = ($form, requiredError, invalidEmailError) => {
      let valid = true;
      let value;
      let field;

      $form
        .find(".has-error")
        .removeClass("has-error")
        .find(".errorlist, .error-block")
        .remove();

      $form.find(".nonfield").remove();

      $form
        .find("input, textarea")
        .not('[type="hidden"]')
        .each(function() {
          value = $(this).val();
          if (!value && $(this).attr("required")) {
            field = $(this)
              .parents(".form-group")
              .addClass("has-error")
              .append($(requiredError));

            valid = false;
          }

          if ($(this).is(`[type="email"]`) && value) {
            if (!utilsObj.validateEmail(value)) {
              $(this)
                .parents(".form-group")
                .addClass("has-error")
                .append($(invalidEmailError));
              valid = false;
            }
          }
        });

      return valid;
    };

    utilsObj.scrollTop = function() {
      $(window).scrollTop(0);
    };

    (() => {
      $("#messages").length ? $("#messages").sticky({ topSpacing: 20 }) : null;
    })();

    (() => {
      $(".btn").on("click mouseup", function(e) {
        $(this).blur();
      });
    })();

    (() => {
      setTimeout(function() {
        new Blazy({
          offset: 200,
          success: elem => {
            setTimeout(() => {
              $(elem).addClass("show");
            }, 10);
          }
        });
      }, 10);
    })();

    (() => {
      let delay = 200;
      $("#messages")
        .find(".alert")
        .each(function(inx, item) {
          $(item)
            .delay(delay * (inx + 2))
            .addClass("in");
        });
    })();

    (() => {
      window.moment.locale($("body").attr("lang"));
    })();

    return utilsObj;
  })());
})(jQuery);

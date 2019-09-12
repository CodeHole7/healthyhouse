($ => {
  "use strict";

  let requiredError = window._radonOptions.requiredError;
  let invalidEmailError = window._radonOptions.invalidEmailError;
  let invalidPhoneError = window._radonOptions.invalidPhoneError;

  const validateForm = $form => {
    let valid = true;
    let value;
    let field;

    $form
      .find(".has-error")
      .removeClass("has-error")
      .find(".errorlist")
      .remove();

    $form.find(".nonfield").remove();

    $form
      .find("input")
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
          if (!_utils.validateEmail(value)) {
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

  $("#register_form")
    .find("input")
    .not('[type="hidden"]')
    .each(function() {
      if (!$(this).attr("val")) {
        $(this).val("");
      }
    });

  $(".register-page form").each(function(indx, item) {
    let $form = $(item);
    let $confirmBtn = $form.find('button[type="submit"]');
    let formValid = false;

    $form[0].onsubmit = function(e) {
      if (formValid) {
        return true;
      } else {
        e.preventDefault();
        var disabled = $confirmBtn.prop("disabled");
        if (!disabled) {
          $confirmBtn.blur();
          if (validateForm($form)) {
            formValid = true;
            $form.submit();
            $confirmBtn.prop("disabled", true);
          }
        }
        return false;
      }
    };
  });

  let tabs = $(".login-logout .section-tab");

  let activeTab = $(".login-logout .section-tab.active");
  $(activeTab.attr("href")).addClass("show");

  tabs.on("click", function(e) {
    e.preventDefault();
    let activeTab;
    tabs.removeClass("active");
    $(".login_form, .register_form").removeClass("show");
    activeTab = $(this);
    activeTab.addClass("active");
    $(activeTab.attr("href")).addClass("show");
  });
})(jQuery);

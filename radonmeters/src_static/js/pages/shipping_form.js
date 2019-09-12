($ => {
  "use strict";

  let $form = $("#new_shipping_address");
  let $confirmBtn = $form.find('button[type="submit"]');
  let formValid = false;

  let requiredError = window._radonOptions.requiredError;
  let invalidEmailError = window._radonOptions.invalidEmailError;
  let invalidPhoneError = window._radonOptions.invalidPhoneError;

  const validateForm = () => {
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

        if ($(this).is(`[name="phone_number_modified"]`) && value) {
          if (!$(this).intlTelInput("isValidNumber")) {
            $(this)
              .parents(".form-group")
              .addClass("has-error")
              .append($(invalidPhoneError));
            valid = false;
          }
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

  $form[0].onsubmit = function(e) {
    if (formValid) {
      return true;
    } else {
      e.preventDefault();
      var disabled = $confirmBtn.prop("disabled");
      if (!disabled) {
        $confirmBtn.blur();
        if (validateForm()) {
          formValid = true;
          $form.submit();
          $confirmBtn.prop("disabled", true);
        }
      }
      return false;
    }
  };

  autosize($form.find("textarea"));
})(jQuery);

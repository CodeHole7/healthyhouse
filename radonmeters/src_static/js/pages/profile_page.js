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
    console.log(valid);
    return valid;
  };

  let renderErrors = (errors, $form) => {
    console.log(errors, $form);
    $form
      .find(".has-error")
      .removeClass("has-error")
      .find(".errorlist")
      .remove();

    $form.find(".nonfield").remove();

    for (let name in errors) {
      if (!errors.hasOwnProperty(name)) {
        return;
      }

      $form
        .find(`[name="${name}"]`)
        .parents(".form-group")
        .addClass("has-error")
        .append(`<ul class="errorlist"><li>${errors[name]}</li></ul> `);
    }
  };

  let submitForm = ($form, $confirmBtn) => {
    $.ajax({
      url: $form[0].action,
      method: $form[0].method,
      data: $form.serialize(),
      beforeSend: function() {
        $confirmBtn.prop("disabled", true);
      },
      error: function(data) {
        $confirmBtn.prop("disabled", false);
        renderErrors(data.responseJSON, $form);
      },
      success: function(data) {
        $form
          .find("input")
          .not('[type="hidden"]')
          .val("");
        _utils.renderMessages("success", data.message);
        setTimeout(function() {
          $confirmBtn.prop("disabled", false);
        }, 5000);
      }
    });
  };

  $("#password_form")
    .find("input")
    .not('[type="hidden"]')
    .each(function() {
      if (!$(this).attr("val")) {
        $(this).val("");
      }
    });

  $(".profile-page form").each(function(indx, item) {
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
            if ($form.is("#profile_form")) {
              formValid = true;
              $form.submit();
            } else {
              submitForm($form, $confirmBtn);
            }

            $confirmBtn.prop("disabled", true);
          }
        }
        return false;
      }
    };
  });
})(jQuery);

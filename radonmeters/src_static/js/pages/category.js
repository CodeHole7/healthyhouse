$($ => {
  "use strict";

  const $form = $("#consultation-form");
  const $confirmBtn = $form.find("button");
  const requiredError = window._radonOptions.requiredError;
  const invalidEmailError = window._radonOptions.invalidEmailError;
  const invalidPhoneError = window._radonOptions.invalidPhoneError;
  const $popup = $("#consultation-form-popup");

  $popup.rm_popup();

  $popup.on("closed:rm_modal", () => {
    $form
      .find("input")
      .not('[type="hidden"]')
      .val("");
    $form
      .find(".has-error")
      .removeClass("has-error")
      .find(".errorlist, .error-block")
      .remove();

    $form.find(".nonfield").remove();
  });

  $(".open-consultation-popup").click(() => {
    $popup.data("rm_popup").show();
  });

  const validateForm = () => {
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

  const renderErrors = errors => {
    $form
      .find(".has-error")
      .removeClass("has-error")
      .find(".errorlist, .error-block")
      .remove();
    for (let name in errors) {
      if (!errors.hasOwnProperty(name)) {
        continue;
      }
      $(this)
        .parents(".form-group")
        .addClass("has-error")
        .append(`<ul class="errorlist"><li>${errors[name]}</li></ul>`);
    }
  };

  var sendRequest = function() {
    $.ajax({
      url: $form[0].action,
      method: $form[0].method,
      data: $form.serialize(),
      beforeSend: function() {
        $confirmBtn.prop("disabled", true);
      },
      error: function(data) {
        $confirmBtn.prop("disabled", false);
        renderErrors(data.responseJSON.errors);
      },
      success: function(data) {
        $popup.off("closed:rm_modal").on("closed:rm_modal", () => {
          _utils.renderMessages("success", data.message);
          $popup.off("closed:rm_modal");
        });
        $popup.data("rm_popup").hide();

        $form
          .find("input")
          .not('[type="hidden"]')
          .val("");
        setTimeout(function() {
          $confirmBtn.prop("disabled", false);
        }, 5000);
      }
    });
  };

  $form[0].onsubmit = function(e) {
    e.preventDefault();
    var disabled = $confirmBtn.prop("disabled");
    if (!disabled) {
      $confirmBtn.blur();
      if (validateForm()) {
        sendRequest();
      }
    }
    return false;
  };

  $(".products-wrapper").each(function(i, el) {
    var $this = $(this);
    setTimeout(function() {
      $this.addClass("show-card");
    }, i * 100);
  });

  $(".pagination-container").addClass("show-container");
});

($ => {
  "use strict";

  const $container = $(".sorting-dropdown");
  const $form = $container.find("form");
  const $select = $form.find("select");
  $container.find("#sort_selector a").on("click", function(e) {
    e.preventDefault();
    if (
      $(this)
        .parent()
        .is(".active")
    ) {
      return;
    }
    $select.val($(this).data("value"));
    $form.submit();
  });
})(jQuery);

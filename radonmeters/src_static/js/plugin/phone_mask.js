(() => {
  "use strict";

  $('[name="phone_number"]').each(function() {
    console.log("------------------------------------");
    console.dir($(this));
    console.log("------------------------------------");
    $(this)
      .attr({ id: "id_phone_number_modified", name: "phone_number_modified" })
      .addClass("phone_input")
      .intlTelInput({
        hiddenInput: "phone_number",
        preferredCountries: ["dk"],
        initialCountry: "dk",
        autoPlaceholder: "aggressive",
        separateDialCode: true,
        onlyCountries: [
          "al",
          "ad",
          "at",
          "by",
          "be",
          "ba",
          "bg",
          "hr",
          "cz",
          "dk",
          "ee",
          "fo",
          "fi",
          "fr",
          "de",
          "gi",
          "gr",
          "va",
          "hu",
          "is",
          "ie",
          "it",
          "lv",
          "li",
          "lt",
          "lu",
          "mk",
          "mt",
          "md",
          "mc",
          "me",
          "nl",
          "no",
          "pl",
          "pt",
          "ro",
          "ru",
          "sm",
          "rs",
          "sk",
          "si",
          "es",
          "se",
          "ch",
          "ua",
          "gb"
        ],
        utilsScript:
          location.origin + "/static/bower/intl-tel-input/build/js/utils.js"
      });
  });
})();

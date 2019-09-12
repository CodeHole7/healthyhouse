(() => {
  'use strict';

  const $autocomplete = $('#autocomplete');
  const $risk_form = $('#risk-form')

  if(!$autocomplete.length) { return; } 
  $risk_form.on('submit', (e) => { e.preventDefault(); return false; })
  const autocomplete = new google.maps.places.Autocomplete($autocomplete[0],
    { types: ["geocode"], componentRestrictions: { country: "dk" } }
  );

  $autocomplete.on('focus', geolocate);
  $('#autocomplete-btn').on('click', inform_risk)

  function inform_risk() {
    var place = autocomplete.getPlace();
    if (place == undefined) return;
    var locality = null;
    for (var i in place.address_components) {
      if ($.inArray("locality", place.address_components[i]["types"]) != -1)
        locality = place.address_components[i]["long_name"].toLowerCase();
    }

    if(!locality) {
      locality = place.address_components[0]["long_name"].toLowerCase();
    }
    _utils.renderMessages();
    $.ajax({
      url: $risk_form.attr('action'),
      method: 'get',
      data: { municipality: locality },
      contentType: "application/json",
      success: function(html) {
        $("#rdncls_ph").html(html["municipality"].charAt(0).toUpperCase() + html["municipality"].slice(1));
        $("#statspan").html(html["level"]);
        $("#avgbq").html(html["avglevel"]);
        $("#radonleveltxt").slideDown();
      },
      error: function(data) {
        _utils.renderMessages('danger', data.responseJSON.detail);
      }
    });
  }

  // Bias the autocomplete object to the user's geographical location,
  // as supplied by the browser's 'navigator.geolocation' object.
  function geolocate() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
        var geolocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        var circle = new google.maps.Circle({
          center: geolocation,
          radius: position.coords.accuracy
        });
        autocomplete.setBounds(circle.getBounds());
      });
    }
  }
})();
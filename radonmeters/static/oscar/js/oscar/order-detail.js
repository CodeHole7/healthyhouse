(($, global) => {
  $('.send-date-payment').on('click', function (e) {
    var url = $('.send-date-payment-form').attr('action');
    var date = $('.send-date-payment-value').val();
    var paid = $('.send-date-payment-paid').is(':checked');
    $.ajax({
      url: url,
      method: 'patch',
      dataType: "json",
      contentType: "application/json",
      data: {
        date_payment: date,
        is_paid: paid
      },
      success: function (resp) {

      },
      error: function (resp) {
        alert(JSON.parse(resp.responseText).name[0])
      }
    });
  });

  $('.send-invoice-accounting-form').on('submit', function (e) {
    e.preventDefault()
    var url = $('.send-invoice-accounting-form').attr('action');

    var formData = new FormData(this);
    var xhr = new XMLHttpRequest();

    xhr.open( 'POST', url, true );
    xhr.onreadystatechange = function ( response ) {
      if (xhr.readyState == 4) {
         if(xhr.status == 200)
           alert('Invoice has been imported.')
         else
          alert(JSON.parse(response.target.responseText)['non_field_errors'])
      }
    };
    xhr.send(formData);

  });
})(jQuery, window);


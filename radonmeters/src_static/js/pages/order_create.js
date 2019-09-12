"use strict";
!function(e){
    e(document).on("change", "#id_status", function(event) {
        if(e(this).val() === "created") {
            e('#serial_number_box').hide();
            e('#serial_number_box').data('values', e('#id_serial_numbers').val());
            e('#id_serial_numbers').val('');
            e('#id_serial_numbers').prop('disabled', true);
        } else {
            e('#id_serial_numbers').val(e('#serial_number_box').data('values'));
            e('#id_serial_numbers').prop('disabled', false);
            e('#serial_number_box').show();
        }
    });
    e(document).on("change", "#id_email", function(event) {
        e.getJSON('/api/v1/users/', {email: e("#id_email").val()}, function (data) {
            if (data['count'] == 1) {
                e('#id_phone_number_modified').val(data['results'][0]['phone_number']);
                e('#id_first_name').val(data['results'][0]['first_name']);
                e('#id_last_name').val(data['results'][0]['last_name']);
                e('#id_phone_number_modified').prop('readonly', true);
                e('#id_first_name').prop('readonly', true);
                e('#id_last_name').prop('readonly', true);
            } else {
                e('#id_phone_number_modified').prop('readonly', false);
                e('#id_first_name').prop('readonly', false);
                e('#id_last_name').prop('readonly', false);
            }
        });
    });
}(jQuery);
$(function() {
    'use strict';

    let option = {
        minimumResultsForSearch: -1,
        width: '100%',
        dropdownCssClass: 'select2-lg',
        containerCssClass: 'select2-container-lg'
    };

    $('.large-select2 select').not('select2-ignore').select2(option);
});

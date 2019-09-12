"use strict";
!function(e){
  e(document).on("keyup", ".dosimeter-editing", function(event) {
    if(event.key === "Enter") {
      e(this).closest("tr").find(".update-dosimeter").click();
      e(this).closest("tr").next("tr").find(".edit-dosimeter").click();
      e(this).closest("tr").next("tr").find('.dosimeter-editing[name="serial_number"]').focus();
    }
    return true;
  });
  e(document).on("keydown", ".dosimeter-editing", function(event) {
    if(event.key === "Enter") {
      event.preventDefault();
      return false;
    }
  });
}(jQuery);
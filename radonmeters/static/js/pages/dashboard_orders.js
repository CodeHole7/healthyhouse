"use strict";!function(e){e(document).on("keyup",".dosimeter-editing",function(t){return"Enter"===t.key&&(e(this).closest("tr").find(".update-dosimeter").click(),e(this).closest("tr").next("tr").find(".edit-dosimeter").click(),e(this).closest("tr").next("tr").find('.dosimeter-editing[name="serial_number"]').focus()),!0}),e(document).on("keydown",".dosimeter-editing",function(e){if("Enter"===e.key)return e.preventDefault(),!1})}(jQuery);
//# sourceMappingURL=dashboard_orders.js.map
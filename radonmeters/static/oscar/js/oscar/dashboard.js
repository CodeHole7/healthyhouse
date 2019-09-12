var oscar = (function(o, $) {
  o.radonmeters = {};

  o.getCsrfToken = function() {
    // Extract CSRF token from cookies
    var cookies = document.cookie.split(";");
    var csrf_token = null;
    $.each(cookies, function(index, cookie) {
      cookieParts = $.trim(cookie).split("=");
      if (cookieParts[0] == "csrftoken") {
        csrf_token = cookieParts[1];
      }
    });
    // Extract from cookies fails for HTML-Only cookies
    if (!csrf_token) {
      csrf_token = $(document.forms.valueOf()).find(
        '[name="csrfmiddlewaretoken"]'
      )[0].value;
    }
    return csrf_token;
  };

  o.dashboard = {
    init: function(options) {
      // Run initialisation that should take place on every page of the dashboard.
      var defaults = {
        languageCode: "en",
        dateFormat: "dd-mm-yyyy",
        timeFormat: "hh:ii",
        maskFormat: "d-m-y",
        datetimeFormat: "dd-mm-yyyy hh:ii",
        stepMinute: 15,
        initialDate: new Date(new Date().setSeconds(0)),
        tinyConfig: {
          entity_encoding: "raw",
          statusbar: false,
          menubar: false,
          plugins: "link lists image",
          style_formats: [
            { title: "Text", block: "p" },
            { title: "Heading", block: "h2" },
            { title: "Subheading", block: "h3" }
          ],
          toolbar:
            "styleselect | bold italic blockquote | bullist numlist | link | image"
        }
      };
      o.dashboard.options = $.extend(true, defaults, options);

      o.dashboard.initWidgets(window.document);
      o.dashboard.initForms();

      $(".category-select ul")
        .prev("a")
        .on("click", function() {
          var $this = $(this),
            plus = $this.hasClass("ico_expand");
          if (plus) {
            $this.removeClass("ico_expand").addClass("ico_contract");
          } else {
            $this.removeClass("ico_contract").addClass("ico_expand");
          }
          return false;
        });

      // Adds error icon if there are errors in the product update form
      $('[data-behaviour="affix-nav-errors"] .tab-pane').each(function() {
        var productErrorListener = $(this)
          .find('[class*="error"]:not(:empty)')
          .closest(".tab-pane")
          .attr("id");
        $('[data-spy="affix"] a[href="#' + productErrorListener + '"]').append(
          '<i class="icon-info-sign pull-right"></i>'
        );
      });

      o.dashboard.filereader.init();
    },
    initWidgets: function(el) {
      /** Attach widgets to form input.
       *
       * This function is called once for the whole page. In that case el is window.document.
       *
       * It is also called when input elements have been dynamically added. In that case el
       * contains the newly added elements.
       *
       * If the element selector refers to elements that may be outside of newly added
       * elements, don't limit to elements within el. Then the operation will be performed
       * twice for these elements. Make sure that that is harmless.
       */
      o.dashboard.initDatePickers(el);
      o.dashboard.initMasks(el);
      o.dashboard.initWYSIWYG(el);
      o.dashboard.initSelects(el);
      o.dashboard.initPhoneMask(el);
    },
    initPhoneMask: function(el) {
      $(el)
        .find('[name="phone_number"]')
        .each(function() {
          $(this)
            .attr({
              id: "id_phone_number_modified",
              name: "phone_number_modified"
            })
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
                location.origin +
                "/static/bower/intl-tel-input/build/js/utils.js"
            });
        });
    },
    initMasks: function(el) {
      setTimeout(function() {
        $(el)
          .find(":input[data-inputmask]")
          .not(".mask-ignore")
          .inputmask({ mask: o.dashboard.options.maskFormat });
      }, 300);
    },
    initSelects: function(el) {
      // Adds type/search for select fields
      var $selects;

      function formatShipmentSelect(state, a) { 
        if (!state.id) return state.text;
        if(state.id === 'does_not_matter') return state.text;
        return "<img class='shipment-options__icons' src='/static/images/shipment_icons/" + state.id + ".png'/>" + state.text;
      }

      $(window).on("load", function() {
        setTimeout(function() {
          $selects = $(el)
            .find("select")
            .not(".no-widget-init select")
            .not(".no-widget-init");
          $selects
            .filter(".form-stacked select")
            .not(".initial-select2-width")
            .css("width", "100%");
          $selects
            .filter(".form-inline select")
            .not(".initial-select2-width")
            .css("width", "300px");
          $('.col-sm-8 > .iti-sdc-3').css('width', '100%')
          $selects.each(function(i, e) {
            var opts = {width: "100%"};
            if(e.getAttribute('name') === 'shipment_status') {
              opts.formatSelection = formatShipmentSelect
              opts.formatResult = formatShipmentSelect
            }
            $(e).select2(opts);
          });
        }, 300);

        $(el)
          .find("input.select2")
          .css("width", "100%")
          .each(function(i, e) {
            var opts = {};
            if ($(e).data("ajax-url")) {
              opts = {
                ajax: {
                  url: $(e).data("ajax-url"),
                  dataType: "json",
                  results: function(data, page) {
                    let name;
                    if ($(e).data("name")) {
                      data.results = data.results.map(function(item) {
                        name =
                          item.first_name +
                          " " +
                          item.last_name +
                          " " +
                          "(" +
                          item.email +
                          ")";
                        return { id: item.id, text: name };
                      });
                    }
                    if ($(e).data("code")) {
                      data.results = data.results.map(function(item) {
                        name = item.first_name + " " + item.last_name;
                        return { id: item.code, text: name };
                      });
                    }
                    if (page == 1 && !($(e).data("required") == "required")) {
                      data.results.unshift({ id: "", text: "------------" });
                    }
                    return data;
                  },
                  data: function(term, page) {
                    return {
                      q: term,
                      page: page
                    };
                  }
                },
                multiple: $(e).data("multiple"),
                initSelection: function(e, callback) {
                  if ($(e).val()) {
                    $.ajax({
                      type: "GET",
                      url: $(e).data("ajax-url"),
                      data: [{ name: "initial", value: $(e).val() }],
                      success: function(data) {
                        var item;
                        if ($(e).data("name")) {
                          item = data.results.filter(function(item) {
                            return $(e).val() == item.id;
                          })[0];
                          item &&
                            callback({
                              id: item.id,
                              text:
                                item.first_name +
                                " " +
                                item.last_name +
                                " " +
                                "(" +
                                item.email +
                                ")"
                            });
                          return;
                        }
                        if (data.results) {
                          if ($(e).data("multiple")) {
                            callback(data.results);
                          } else {
                            callback(data.results[0]);
                          }
                        }
                      },
                      dataType: "json"
                    });
                  }
                }
              };
            }
            $(e).select2(opts);
          });
      });
    },
    autocomplete: {
      init: function (storageName, conf) {
          var that = oscar.dashboard.autocomplete
          var inputAutocomplete
          that.storageName = storageName
          that[storageName] = {};
          that[storageName].xhr = null;
          inputAutocomplete = $('input.autocomplete')

          if(inputAutocomplete.length) {
              inputAutocomplete.each(function() {
                  var $input = $(this);
                  var $btnSave = $input.next('.input-group-btn').find('.js-save-word');
                  var value = '';
                  var to = null;

                  if ($btnSave) {
                      that.toggleSaveBtn($input, $btnSave);
                      $input.on('input', function () {
                          that.toggleSaveBtn($input, $btnSave);
                      });

                      $btnSave.click(function () {
                          if($input.prop('disabled')) {return;}
                          value = $input.val();
                          if(!value.trim()) {return;}
                          $.ajax(conf.createUrl, {
                              method: 'post',
                              dataType: "json",
                              traditional: true,
                              data: JSON.stringify({
                                  name: value
                              }),
                              beforeSend: function(xhr, settings) {
                                  xhr.setRequestHeader("X-CSRFToken", o.getCsrfToken());
                                  xhr.setRequestHeader("Content-Type", 'application/json; charset=utf-8');
                                  $input.parent().removeClass('has-success');
                              },
                              success: function (resp) {
                                  if(to) {return}
                                  $input.parent().addClass('has-success');
                                  to = setTimeout(function () {
                                      $input.parent().removeClass('has-success');
                                      clearTimeout(to);
                                      to = null;
                                  }, 1500)
                              },
                              error: function (resp) {
                                  alert(JSON.parse(resp.responseText).name[0])
                              }
                          });
                      });
                  }

                  $input.autoComplete({
                      minChars: 1,
                      cache: false,
                      renderItem: function (item, search){
                          search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                          var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
                          var deletePart = '';
                          if (conf.deleteUrl) {
                              deletePart = '<a class="fa fa-trash delete-word js-delete-word"></a>';
                          };
                          var html = '<div class="autocomplete-suggestion" data-id="'+ item.id +'" data-val="' + item[conf.key] + '">' +
                              item[conf.key].replace(re, "<b>$1</b>") +
                              deletePart +
                          '</div>';

                          return html
                      },
                      source: function(term, suggest){
                          try { that[storageName].xhr.abort(); } catch(e){}
                          that[storageName].xhr = $.getJSON(conf.getUrl, {
                              q: term
                          }, function (data) { suggest(data.results) });
                      },
                      onSelect: function(event, term, item){
                          var $target = $(event.target)
                          if($target.hasClass('js-delete-word')) {
                              $.ajax(conf.deleteUrl.replace('{id}', item.attr('data-id')), {
                                  method: 'delete',
                                  dataType: "json",
                                  traditional: true,
                                  data: JSON.stringify({}),
                                  beforeSend: function(xhr, settings) {
                                      xhr.setRequestHeader("X-CSRFToken", o.getCsrfToken());
                                      xhr.setRequestHeader("Content-Type", 'application/json; charset=utf-8');
                                  },
                                  success: function (resp) {
                                      $input.val('');
                                      alert(conf.removedMsg.replace('{name}', '"' + item.attr('data-val') + '"'));
                                  },
                                  error: function (resp) {
                                      alert(JSON.parse(resp.responseText).name[0])
                                  }
                              });
                          }
                      }
                  });
          });
        }
      },
      toggleSaveBtn: function($input, $btnSave) {
        if ($input.val().trim()) {
          $btnSave.prop("disabled", false);
        } else {
          $btnSave.prop("disabled", true);
        }
      },
      processResponse: function(data) {
        var that = oscar.dashboard.autocomplete;
      }
    },
    initDatePickers: function(el) {
      if ($.fn.datetimepicker) {
        var defaultDatepickerConfig = {
          format: o.dashboard.options.dateFormat,
          autoclose: true,
          language: o.dashboard.options.languageCode,
          minView: 2
        };
        $dates = $(el)
          .find('[data-oscarWidget="date"]')
          .not(".no-widget-init")
          .not(".no-widget-init *");
        $dates.each(function(ind, ele) {
          var $ele = $(ele),
            config = $.extend({}, defaultDatepickerConfig, {});
          $ele.datetimepicker(config);
        });

        var defaultDatetimepickerConfig = {
          format: o.dashboard.options.datetimeFormat,
          minuteStep: o.dashboard.options.stepMinute,
          autoclose: true,
          language: o.dashboard.options.languageCode,
          initialDate: o.dashboard.options.initialDate
        };
        $datetimes = $(el)
          .find('[data-oscarWidget="datetime"]')
          .not(".no-widget-init")
          .not(".no-widget-init *");
        $datetimes.each(function(ind, ele) {
          var $ele = $(ele),
            config = $.extend({}, defaultDatetimepickerConfig, {
              minuteStep: $ele.data("stepminute")
            });
          $ele.datetimepicker(config);
        });

        var defaultTimepickerConfig = {
          format: o.dashboard.options.timeFormat,
          minuteStep: o.dashboard.options.stepMinute,
          autoclose: true,
          language: o.dashboard.options.languageCode,
          initialDate: o.dashboard.options.initialDate
        };
        $times = $(el)
          .find('[data-oscarWidget="time"]')
          .not(".no-widget-init")
          .not(".no-widget-init *");
        $times.each(function(ind, ele) {
          var $ele = $(ele),
            config = $.extend({}, defaultTimepickerConfig, {
              minuteStep: $ele.data("stepminute"),
              startView: 1,
              maxView: 1,
              formatViewType: "time"
            });
          $ele.datetimepicker(config);
        });
      }
    },
    initWYSIWYG: function(el) {
      var r = /^<script[\s\S]*?>[\s\S]*?<\/script>/gi;
      $textareas = $(el)
        .find("textarea")
        .not(".no-widget-init textarea")
        .not(".no-widget-init");
      $textareas.each(function() {
        CKEDITOR.replace(this, {
          toolbar: "standard",
          width: "100%",
          basicEntities: false,
          disallowedContent: "script; *[on*]",
          on: {
            paste: function(evt) {
              var editor = evt.editor,
                data;
              try {
                data = evt.data.dataTransfer._.data.Text;
                if (r.test(data)) {
                  editor.setData("<p>scripts are not allowed</p>");
                }
              } catch (err) {
                console.warn(err);
              }
            }
          },
          filebrowserUploadUrl: "/ckeditor/upload/",
          filebrowserBrowseUrl: "/ckeditor/browse/"
        });
      });
    },
    initForms: function() {
      // Disable buttons when they are clicked and show a "loading" message taken from the
      // data-loading-text attribute (http://getbootstrap.com/2.3.2/javascript.html#buttons).
      // Do not disable if button is inside a form with invalid fields.
      // This uses a delegated event so that it keeps working for forms that are reloaded
      // via AJAX: https://api.jquery.com/on/#direct-and-delegated-events
      $(document.body).on("click", "[data-loading-text]", function() {
        var form = $(this).parents("form");
        if (!form || $(":invalid", form).length == 0) $(this).button("loading");
      });
    },
    offers: {
      init: function() {
        oscar.dashboard.offers.adjustBenefitForm();
        $("#id_type").change(function() {
          oscar.dashboard.offers.adjustBenefitForm();
        });
      },
      adjustBenefitForm: function() {
        var type = $("#id_type").val(),
          $valueContainer = $("#id_value").parents(".control-group");
        if (type == "Multibuy") {
          $("#id_value").val("");
          $valueContainer.hide();
        } else {
          $valueContainer.show();
        }
      }
    },
    product_attributes: {
      init: function() {
        var type_selects = $("select[name$=type]");

        type_selects.each(function(index) {
          o.dashboard.product_attributes.toggleOptionGroup($(this));
        });

        type_selects.change(function(e) {
          o.dashboard.product_attributes.toggleOptionGroup($(this));
        });
      },

      toggleOptionGroup: function(type_select) {
        var option_group_select = $(
          "#" + type_select.attr("id").replace("type", "option_group")
        );
        var v = type_select.val();
        option_group_select
          .select2("container")
          .toggle(v === "option" || v === "multi_option");
      }
    },
    ranges: {
      init: function() {
        $('[data-behaviours~="remove"]').click(function() {
          $this = $(this);
          $this
            .parents("table")
            .find("input")
            .prop("checked", false);
          $this
            .parents("tr")
            .find("input")
            .prop("checked", true);
          $this.parents("form").submit();
        });
      }
    },
    createOrder: {
      disableForm: false,
      createOrderInit: function(redirect, msg) {
        var u = o.dashboard.createOrder;
        u.$saveBtn = $(".submit-form");
        u.$form = $("#create-order");
        u.csrf = $('[name="csrfmiddlewaretoken"]').val();
        u.redirect = redirect;
        u.msg = msg;

        u.$form.submit(function(e) {
          e.preventDefault();
          u.submitForm(u);

          return false;
        });
      },
      submitForm: function(u) {
        if (u.disableForm) return;

        u.clearError();
        u.$saveBtn.prop("disabled", true);
        u.disableForm = true;
        var data = {},
          name,
          type,
          value;
        u.$form.find("input, select").each(function() {
          name = $(this).attr("name");
          type = $(this).attr("data-type");
          value = $(this).val();
          if (name) {
            switch (type) {
              case "array":
                if (!!value) {
                  data[$(this).attr("name")] = value
                    .split(",")
                    .map(function(item) {
                      return $.trim(item);
                    });
                }
                break;
              default:
                if (!((name == "phone_number") && !$("#id_phone_number_modified").val())) {
                    if (name == "phone_number" && $("#id_phone_number_modified").val()[0] == "+") {
                        data[$(this).attr("name")] = $("#id_phone_number_modified").val();
                    } else {
                        if (!!value) data[$(this).attr("name")] = value;
                    }
                }
                break;
            }
          }
        });
        $.ajax(u.$form.attr("action"), {
          method: "post",
          dataType: "json",
          traditional: true,
          data: JSON.stringify(data),
          beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", o.getCsrfToken());
            xhr.setRequestHeader(
              "Content-Type",
              "application/json; charset=utf-8"
            );
          },
          success: function(resp) {
            window.alert(u.msg);
            window.location.href = u.redirect;
          },
          error: function(resp) {
            o.messages.clear();
            if (JSON.parse(resp.responseText).detail) {
              o.messages.error(JSON.parse(resp.responseText).detail);
            } else {
              u.renderError(JSON.parse(resp.responseText));
            }
            u.$saveBtn.prop("disabled", false);
            u.disableForm = false;
          }
        }).always(function() {
          u.$saveBtn.prop("disabled", false);
          u.disableForm = false;
        });
      },
      renderError: function(errors) {
        for (name in errors) {
          if (!errors.hasOwnProperty(name)) continue;
          $('[name="' + name + '"]')
            .closest(".form-group")
            .find(".error-block")
            .text(errors[name].join(", "));
        }
      },
      clearError: function() {
        $(".error-block").text("");
      }
    },
    orders: {
      csrf_token: null,
      $table: $("form > table"),
      $dosimetersRow: $(".dosimeters-row"),
      $dosimeterItem: $(".dosimeter-item"),
      $resentModal: $("#ResentMailModal"),
      $forceApproveModal: $("#ForceApproveModal"),
      initTabs: function() {
        if (location.hash) {
          $(".nav-tabs a[href=" + location.hash + "]").tab("show");
        }
      },
      initTable: function(opt) {
        var that = this;
        var table = $("form > table"),
          input = $('<input type="checkbox" />').css({
            "margin-right": "5px",
            "vertical-align": "top"
          });
        $("th:first", table).prepend(input);
        $(input).change(function() {
          $("tr", table).each(function() {
            $("input.selected_order", this).prop(
              "checked",
              $(input).is(":checked")
            );
          });
        });

        that.togglingDosimeterRow();
        that.editTable();
        that.openConfirmationModal();

        this.$table.on("click", ".edit-dosimeter", function() {
          var row = $(this).closest(".dosimeter-item");
          that.toggleFields(row, false);
          var table = this.parentNode.parentNode.parentNode.parentNode.querySelectorAll('.update-dosimeter');
          var count = 0;
          for (var i = 0; i < table.length; i++) {
            if (!table[i].classList.contains('hidden')) {
              count++
            }
          }
          if (count > 1) {
            $('.save-all-dosimeter').removeClass('hidden')
          } else  {
            $('.save-all-dosimeter').addClass('hidden')
          }
        });

        this.$table.on("click", ".edit-all-dosimeter", function(e) {
          e.preventDefault();
          $('.save-all-dosimeter').removeClass('hidden')
          var table = this.parentNode.parentNode.parentNode.parentNode.querySelectorAll('.edit-dosimeter');
          for (var button of table ) {
            button.click()
          }
        });

        this.$table.on("click", ".save-all-dosimeter", function(e) {
          e.preventDefault();
          var table = this.parentNode.parentNode.parentNode.parentNode.querySelectorAll('.update-dosimeter');
          for (var button of table ) {
            button.click()
          }
          $('.save-all-dosimeter').addClass('hidden')
        });

        this.$table.on("click", ".js-set-all-btn", function() {
          var input = $(this)
            .closest("th")
            .find("input");
          var value = input.val();
          if (!value) return;
          var r = confirm(opt.confirmMsg);
          if (r == true) {
            var target = input.data("target");

            $(this)
              .closest(".dosimeters-row")
              .find(target)
              .val(value);
            input.blur().val("");
          }
        });

        this.$table.on("click", ".js-set-all-active-btn", function() {
          var input = $(this)
            .closest("th")
            .find("input");
          var value = input.val();
          if (!value) return;
          var target = input.data("target");

          $(this)
            .closest(".dosimeters-row")
            .find(target)
            .not(":disabled")
            .val(value);
          input.blur().val("");
        });
      },
      initSuperownerSelection: function(args) {
        var url,
          that = this;
        $(".js-submit-superowner").on("click", function() {
          url = $(this).data("url");
          $.ajax(url, {
            method: "PATCH",
            data: { owner: $("input.js-owner-select").val() },
            success: function(resp) {
              o.messages.clear();
              o.messages.success(args.success);
            },
            error: function(resp) {
              o.messages.clear();
              o.messages.error(JSON.parse(resp.responseText).details);
            }
          });
        });
      },
      openConfirmationModal: function() {
        var url,
          that = this;
        this.$table.on("click", ".send-invoice-dosimeter", function(e) {
          url = $(e.target).data("url");
          that.sendInvoice(url);
          that.$resentModal.modal("show");
        });
      },
      sendInvoice: function(url) {
        var that = this;
        that.$resentModal
          .find(".submit-resend")
          .off()
          .on("click", function() {
            $.ajax(url, {
              method: "POST",
              success: function(resp) {
                o.messages.clear();
                o.messages.success(resp.detail);
              },
              error: function(resp) {
                o.messages.clear();
                o.messages.error(JSON.parse(resp.responseText).details);
              },
              xhrFields: {
                onprogress: oscar.dashboard.orders.progressBar.onprogress
              }
            }).always(function() {
              that.$resentModal.modal("hide");
              setTimeout(function() {
                oscar.dashboard.orders.progressBar.hide();
              }, 1000);
            });
          });
      },
      approveDosimeter: function() {
        var url, btn, id;
        var that = this;
        this.$table.on("click", ".approve-dosimeter", function() {
          btn = $(this);
          url = btn.data("url");
          id = btn.data("id");
          var data = {};
          if (o.radonmeters.batchOff) {
            oscar.dashboard.orders.progressBar.show();
          } else {
            data = {
              not_weird_explanation: "Overridden during batch approval",
              ignore_outlier: $('input[name="ignore_outlier"]').prop("checked"),
              ignore_overlap_1: $('input[name="ignore_overlap_1"]').prop(
                "checked"
              ),
              ignore_overlap_2: $('input[name="ignore_overlap_2"]').prop(
                "checked"
              )
            };
          }
          $.ajax(url, {
            method: "POST",
            dataType: "json",
            contentType: "application/json",
            data: data,
            success: function(resp) {
              btn
                .parent()
                .find(".user-who-approved b")
                .text(resp.user_who_approved);
              btn
                .parent()
                .find(".js-approved-at")
                .removeClass("hidden")
                .find("b")
                .text(resp.approved_date);
              btn
                .parent()
                .find("br")
                .remove();

              btn.hide();
              $('.js-send-report[data-id="' + id + '"]').prop(
                "disabled",
                false
              );
              if (o.radonmeters.batchCounter > 0) {
                o.radonmeters.batchCounter -= 1;
                if (o.radonmeters.batchCounter == 0) {
                  o.radonmeters.batchOff = true;
                  oscar.dashboard.orders.progressBar.hide();
                }
              }
            },
            error: function(resp) {
              if (o.radonmeters.batchOff) {
                o.messages.clear();
              }
              var result = JSON.parse(resp.responseText);
              if (result.forceApprove && o.radonmeters.batchOff) {
                $("#weirdnessReasonMessage").html(result.details);
                that.$forceApproveModal
                  .find(".submit-approve")
                  .off()
                  .on("click", function() {
                    var data = {
                      not_weird_override: true,
                      not_weird_explanation: $("#NotWeirdText").val()
                    };
                    $.ajax(url, {
                      method: "POST",
                      dataType: "json",
                      contentType: "application/json",
                      data: data,
                      success: function(resp) {
                        btn
                          .parent()
                          .find(".user-who-approved b")
                          .text(resp.user_who_approved);
                        btn
                          .parent()
                          .find(".user-who-approved b")
                          .append(
                            '<a href="#" title="' +
                              resp.not_weird_explanation +
                              '">*</a>'
                          );
                        btn
                          .parent()
                          .find(".js-approved-at")
                          .removeClass("hidden")
                          .find("b")
                          .text(resp.approved_date);
                        btn
                          .parent()
                          .find("br")
                          .remove();

                        btn.hide();
                        $('.js-send-report[data-id="' + id + '"]').prop(
                          "disabled",
                          false
                        );
                      },
                      error: function(resp) {
                        o.messages.clear();
                        o.messages.error(JSON.parse(resp.responseText).details);
                      },
                      xhrFields: {
                        onprogress:
                          oscar.dashboard.orders.progressBar.onprogress
                      }
                    }).always(function() {
                      that.$forceApproveModal.modal("hide");
                      setTimeout(function() {
                        oscar.dashboard.orders.progressBar.hide();
                      }, 1000);
                    });
                  });
                that.$forceApproveModal.modal("show");
              } else {
                o.messages.error(result.details);
                if (o.radonmeters.batchCounter > 0) {
                  o.radonmeters.batchCounter -= 1;
                  if (o.radonmeters.batchCounter == 0) {
                    o.radonmeters.batchOff = true;
                    oscar.dashboard.orders.progressBar.hide();
                  }
                }
              }
            },
            xhrFields: {
              onprogress: oscar.dashboard.orders.progressBar.onprogress
            }
          }).always(function() {
            setTimeout(function() {
              if (o.radonmeters.batchOff) {
                oscar.dashboard.orders.progressBar.hide();
              }
            }, 1000);
          });
        });
      },
      toggleExternalReport: function() {
        this.$table.on("click", ".toggle-external-report", function() {
          var url, checkbox;
          checkbox = $(this);
          var order_id = checkbox.data("order-id");
          url = checkbox.data("url");
          var data = new FormData($('.upload-external-report-form[data-order-id="'+order_id+'"]')[0]);
          if (checkbox.prop('checked')) {
            data.append('use_external_report', 'checked');
          }
          $.ajax({
            method: 'post',
            url: url,
            data: data,
            processData: false,
            contentType: false,
            error: function(response) {
              o.messages.clear();
              var errorObj = JSON.parse(response.responseText);
              if (errorObj.detail) {
                o.messages.error(errorObj.detail);
                return;
              }
              o.messages.error("Something going wrong. Please, try again");
            }
          });
        });
      },
      sendReport: function(sentMsg) {
        var url, btn, id;
        this.$table.on("click", ".js-send-report", function() {
          btn = $(this);
          url = btn.data("url");
          id = btn.data("id");
          if (o.radonmeters.batchOff) {
            oscar.dashboard.orders.progressBar.show();
          }
          $.ajax(url, {
            method: "POST",
            success: function(resp) {
              btn
                .parent()
                .find(".js-is-report-sent")
                .text(sentMsg + " " + resp.sent_date);
              if (o.radonmeters.batchOff) {
                console.log(o.radonmeters.batchOff, "sent");
                alert(resp.detail);
              }
              if (o.radonmeters.batchCounter > 0) {
                o.radonmeters.batchCounter -= 1;
                if (o.radonmeters.batchCounter == 0) {
                  o.radonmeters.batchOff = true;
                  oscar.dashboard.orders.progressBar.hide();
                }
              }
            },
            error: function(resp) {
              if (o.radonmeters.batchOff) {
                o.messages.clear();
              }
              o.messages.error(JSON.parse(resp.responseText).details);
              if (o.radonmeters.batchOff) {
                alert(JSON.parse(resp.responseText).details);
              }
              if (o.radonmeters.batchCounter > 0) {
                o.radonmeters.batchCounter -= 1;
                if (o.radonmeters.batchCounter == 0) {
                  o.radonmeters.batchOff = true;
                  oscar.dashboard.orders.progressBar.hide();
                }
              }
            },
            xhrFields: {
              onprogress: oscar.dashboard.orders.progressBar.onprogress
            }
          }).always(function() {
            setTimeout(function() {
              if (o.radonmeters.batchOff) {
                oscar.dashboard.orders.progressBar.hide();
              }
            }, 1000);
          });
        });
      },
      isValid: function(date) {
        return (
          !/_/i.test(date) &&
          moment(date, o.dashboard.options.dateFormat.toUpperCase()).isValid()
        );
      },

      editTable: function() {
        var dosimeter,
          data,
          id,
          that = this;
        this.$dosimeterItem.on("click", ".update-dosimeter", function() {
          dosimeter = $(this).closest(".dosimeter-item");
          id = dosimeter.data("id");
          dosimeter.find(".js-server-error").remove();
          dosimeter.find(".error-block").addClass("hidden");
          dosimeter
            .find("#dosimeter_date_from-" + id)
            .parent()
            .removeClass("has-error");
          dosimeter
            .find("#dosimeter_date_to-" + id)
            .parent()
            .removeClass("has-error");
          var measurement_start_date = dosimeter
            .find("#dosimeter_date_from-" + id)
            .val();
          var measurement_end_date = dosimeter
            .find("#dosimeter_date_to-" + id)
            .val();
          var floor = JSON.parse(
            dosimeter.find("#dosimeter-floor-" + id).val()
          );

          if (measurement_start_date && !that.isValid(measurement_start_date)) {
            dosimeter
              .find("#dosimeter_date_from-" + id)
              .parent()
              .addClass("has-error")
              .find(".error-block")
              .removeClass("hidden");
            return;
          }

          if (measurement_end_date && !that.isValid(measurement_end_date)) {
            dosimeter
              .find("#dosimeter_date_to-" + id)
              .parent()
              .addClass("has-error")
              .find(".error-block")
              .removeClass("hidden");
            return;
          }

          data = {
            measurement_start_date:
              measurement_start_date && that.isValid(measurement_start_date)
                ? measurement_start_date
                : "",
            measurement_end_date:
              measurement_end_date && that.isValid(measurement_end_date)
                ? measurement_end_date
                : "",
            floor: floor,
            location: dosimeter.find("#dosimeter-location-" + id).val(),
            uncertainty: dosimeter.find("#dosimeter-uncertainty-" + id).val(),
            concentration: dosimeter
              .find("#dosimeter-concentration-" + id)
              .val(),
            active_area: dosimeter.find("#id_active_area-" + id).is(":checked"),
            use_raw_concentration: dosimeter
              .find("#id_use_raw_concentration-" + id)
              .is(":checked"),
            is_active: dosimeter.find("#id_is_active-" + id).is(":checked"),
            serial_number: dosimeter.find('#dosimeter_serial_number-' + id).val(),
          };

          that.patch(dosimeter.data("url"), data, dosimeter);
          that.toggleFields(dosimeter, true);
          var table = this.parentNode.parentNode.parentNode.parentNode.querySelectorAll('.update-dosimeter');
          var count = 0;
          for (var i = 0; i < table.length; i++) {
            if (!table[i].classList.contains('hidden')) {
              count++
            }
          }
          if (count > 1) {
            $('.save-all-dosimeter').removeClass('hidden')
          } else {
            $('.save-all-dosimeter').addClass('hidden')
          }
        });
      },
      patch: function(url, data, dosimeter) {
        oscar.dashboard.orders.progressBar.show();
        $.ajax(url, {
          method: "PATCH",
          data: data,
          xhrFields: {
            onprogress: oscar.dashboard.orders.progressBar.onprogress
          },
          success: function(data) {
            dosimeter
              .find(".concentration-visual")
              .text(
                data.concentration_visual ? data.concentration_visual : "-"
              );
            dosimeter
              .find(".uncertainty-visual")
              .text(data.uncertainty_visual ? data.uncertainty_visual : "-");
            dosimeter
              .closest(".dosimeters-row")
              .find(".yearly-avg-visual")
              .text(
                data.avg_concentration_visual
                  ? data.avg_concentration_visual
                  : "-"
              );
            // Reset approval status
            btn = dosimeter
              .closest(".dosimeters-row")
              .prev()
              .find(".approve-dosimeter");
            btn
              .parent()
              .find(".user-who-approved b")
              .text("-");
            btn
              .parent()
              .find(".js-approved-at")
              .addClass("hidden");
            btn
              .parent()
              .find("br")
              .remove();
            btn.after("<br/><br/>");
            btn.show();
            btn
              .closest(".order-row")
              .find(".js-send-report")
              .prop("disabled", true);
            // Update order status
            $.ajax(dosimeter.closest("tr.dosimeters-row").prev("tr.order-row").data("url"), {
              method: "GET",
              success: function(data) {
                console.log(data.status);
                if (dosimeter.closest("tr.dosimeters-row").prev("tr.order-row").find("td.order-status").text() != data.status) {
                  dosimeter.closest("tr.dosimeters-row").prev("tr.order-row").find("td.order-status").text('***'+data.status+'***');
                  setTimeout(function() {
                    dosimeter.closest("tr.dosimeters-row").prev("tr.order-row").find("td.order-status").text(data.status);
                  }, 1000);
                }
              }
            });
          },
          error: function(resp) {
            var obj = JSON.parse(resp.responseText);

            for (k in obj) {
              if (!obj.hasOwnProperty(k)) continue;
              dosimeter
                .find("[data-name=" + k + "]")
                .parent()
                .addClass("has-error")
                .append(
                  '<span class="error-block js-server-error"><i class="icon-exclamation-sign"></i>' +
                    obj[k] +
                    "</span>"
                );
            }
            console.log();
          }
        }).always(function() {
          setTimeout(function() {
            oscar.dashboard.orders.progressBar.hide();
          }, 1000);
        });
      },
      togglingDosimeterRow: function() {
        var that = this;
        $(".order-row")
          .on("click", function(e) {
            if (e.target.tagName !== "TD") return;
            var target = $("[" + $(this).data("target") + "]");
            that.$dosimetersRow.each(function() {
              if (this !== target[0]) {
                $(this)
                  .addClass("hidden")
                  .find(".mask")
                  .inputmask("remove");
                that.toggleFields($(this), true);
              }
            });
            target.toggleClass("hidden");
            target
              .find(".mask")
              .inputmask({ mask: o.dashboard.options.maskFormat });
          })
          .css("cursor", "pointer");
      },

      toggleFields: function(root, bool) {
        root.find("select").prop("disabled", bool);
        root
          .find("input")
          .not(".no-disable")
          .prop("disabled", bool);
        root.find(".edit-dosimeter").toggleClass("hidden", !bool);
        root.find(".update-dosimeter").toggleClass("hidden", bool);
      },
      bindCreateShipment: function(view_shipment_template, csrf_token) {
        var $view_shipment;
        var createShipment = function() {
          var that = $(this),
            order_id = that.data("order-id"),
            url = that.data("url"),
            initialText = that.text();
          that.button("loading");
          $.ajax({
            type: "post",
            dataType: "json",
            url: url,
            data: {
              csrfmiddlewaretoken: csrf_token,
              order: order_id
            },
            cache: false,
            success: function(response) {
              $view_shipment = $(view_shipment_template).attr(
                "href",
                response.url
              );
              that.closest('tr').find(".js-create-label").removeClass("hide");
              that.replaceWith($view_shipment);
              o.messages.clear();
              o.messages.success(response.message);
            },
            error: function(response) {
              that.button("loaded").text(initialText);
              //o.messages.clear();
              var errorObj = JSON.parse(response.responseText);
              if (errorObj.errors && errorObj.errors.__all__) {
                errorObj.errors.__all__.forEach(function(error) {
                  o.messages.error(error);
                });
                return;
              }
              o.messages.error("Something going wrong. Please, try again");
            }
          });
        };
        $(".js-create-shipment").click(createShipment);
      },
      progressBar: {
        holder: $(".progress").css({
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          borderRadius: 0
        }),
        bar: $(".progress-bar"),
        onprogress: function(e) {
          var pr;
          if (e.lengthComputable) {
            pr = ((e.loaded / e.total) * 100).toFixed() + "%";
            oscar.dashboard.orders.progressBar.bar.css("width", pr).text(pr);
          }
        },
        hide: function() {
          this.holder.addClass("hidden");
          this.reset();
        },
        show: function() {
          this.holder.removeClass("hidden");
        },
        reset: function() {
          this.bar.css("width", "0%").text("0%");
        }
      },
      bindDownload: function(urls) {
        var ids = [];
        var downloadHandler = function() {
          var that = $(this),
            type = that.data("type"),
            typeOfFile = that.data("object"),
            order_id = that.data("order-id"),
            params = window.location.search,
            url,
            initialText;
          url = urls[typeOfFile];
          if (type === "bulk") {
            url += params;
            if (ids.length) {
              url += params ? "&" : "?";
              url += ids.join("&");
            }
          } else {
            url += "?order_number=" + order_id;
          }
          $.ajax({
            type: "GET",
            url: url,
            cache: false,
            beforeSend: function() {
              oscar.dashboard.orders.progressBar.show();
              if (type === "single") {
                initialText = that.text();
                that.button("loading");
              }
            },
            success: function(response) {
              window.location = url;
            },
            error: function(response) {
              oscar.dashboard.orders.progressBar.hide();
              o.messages.clear();
              var errorObj = JSON.parse(response.responseText);
              if (errorObj.detail) {
                o.messages.error(errorObj.detail);
                return;
              }
              o.messages.error("Something going wrong. Please, try again");
            },
            xhrFields: {
              onprogress: oscar.dashboard.orders.progressBar.onprogress
            }
          }).always(function() {
            if (type === "single") {
                that.button("loaded").text(initialText);
            }
            setTimeout(function() {
              oscar.dashboard.orders.progressBar.hide();
            }, 1000);
          });
        };
        $(".js-order-download").click(downloadHandler);
        $(".selected_order").change(function() {
          if ($(this).prop("checked")) {
            ids.push("order_id=" + $(this).val());
          } else {
            ids.splice(ids.indexOf("order_id=" + $(this).val()), 1);
          }
        });
        $("th:first input").change(function() {
          if ($(this).prop("checked")) {
            $("input.selected_order").each(function() {
              ids.push("order_id=" + $(this).val());
            });
          } else {
            ids = [];
          }
        });
      },
      bindSend: function(urls) {
        var ids = []; //----
        console.log(urls)
        var sendHandler = function() {
          var that = $(this),
            type = that.data("type"),
            typeOfFile = that.data("object"),
            order_id = that.data("order-id"),
            dataUrl = that.data("url"),
            params = window.location.search,
            url,
            fiendParent,
            updateReport = false,
            initialText;
          url = urls[typeOfFile];
          if (type === "bulk") {
            url += params;
            if (ids.length) {
              url += params ? "&" : "?";
              url += ids.join("&");
            }
          } else {
            url += "?order_number=" + order_id;
          }
          oscar.dashboard.orders.progressBar.show();
          if (type === "single") {
            initialText = that.text();
            that.button("loading");
          }
          if (dataUrl) {
              updateReport = true;
              url = dataUrl;
              fiendParent = url.split('/').slice(0,-2).join('/');
          }
          $.ajax({
            type: "post",
            url: url,
            cache: false,
            success: function(response) {
              o.messages.clear();
              o.messages.success(response.detail);
              if (updateReport) {
                  var res = 'The report was sent ' + response.sent_date;
                  document.getElementById(url).innerText = res
              }
            },
            error: function(response) {
              oscar.dashboard.orders.progressBar.hide();
              o.messages.clear();
              var errorObj = JSON.parse(response.responseText);
              if (errorObj.detail) {
                o.messages.error(errorObj.detail);
                return;
              }
              o.messages.error("Something going wrong. Please, try again");
            },
            xhrFields: {
              onprogress: oscar.dashboard.orders.progressBar.onprogress
            }
          }).always(function() {
            setTimeout(function() {
              oscar.dashboard.orders.progressBar.hide();
            }, 1000);
            if (type === "single") {
              that.button("loaded").text(initialText);
            }
          });
        };
        $(".js-order-send").click(sendHandler);
        $(".selected_order").change(function() {
          if ($(this).prop("checked")) {
            ids.push("order_id=" + $(this).val());
          } else {
            ids.splice(ids.indexOf("order_id=" + $(this).val()), 1);
          }
        });
        $("th:first input").change(function() {
          if ($(this).prop("checked")) {
            $("input.selected_order").each(function() {
              ids.push("order_id=" + $(this).val());
            });
          } else {
            ids = [];
          }
        });
      },

      bindPrint: function(urls) {
          var ids = [];
          var pdfjsLib = window['pdfjs-dist/build/pdf'];
          // pdfjsLib.GlobalWorkerOptions.workerSrc = '//mozilla.github.io/pdf.js/build/pdf.worker.js';
          var printHandler = function () {
              var that = $(this),
                  type = that.data("type"),
                  typeOfFile = that.data("object"),
                  order_id = that.data("order-id"),
                  params = window.location.search,
                  url,
                  initialText,
                  ua = navigator.userAgent;
              url = urls[typeOfFile];
              if (type === "bulk") {
                  url += params;
                  if (ids.length) {
                      url += params ? "&" : "?";
                      url += ids.join("&");
                  }
              } else {
                  url += "?order_number=" + order_id;
              }
              $.ajax({
                  type: "GET",
                  url: url,
                  headers: {
                      "Content-type": "application/pdf"
                  },
                  cache: false,
                  success: function (response) {
                      if (ua.search(/Firefox/) > -1 || ua.indexOf("MSIE")!=-1) {
                          printPdfFile(url)
                      } else {
                          printJS({printable: window.location.origin+url, type:'pdf', showModal:true})
                      }
                  },
                  error: function (response) {
                      o.messages.clear();
                      o.messages.error("Something going wrong. Please, try again");
                  },
                  xhrFields: {
                      onprogress: oscar.dashboard.orders.progressBar.onprogress
                  }
              })
          }

          function printPdfFile(file) {
              var printableDocument = document.createElement('div');
              var pages = []
              var pagesCount = 1;
              var currentPageNum = 0;
              var printWindowName = Date.now().toString() + Math.random().toString()

              function openPrintable() {
                  window[printWindowName] = window.open("", "Print");
                  window[printWindowName].onunload = function () {
                      console.log('close print page', printWindowName)
                  }
                  window[printWindowName].onload = function () {
                      console.log('open print window', printWindowName)
                      window[printWindowName].print()
                  }

                  pages.forEach(function (item) {
                      printableDocument.appendChild(item)
                  })

                  window[printWindowName].document.body.appendChild(printableDocument)
                  window[printWindowName].print()
              }

              function renderPage (page, num) {
                  var scale = 1.5;
                  var viewport = page.getViewport(scale);
                  var canvasEl = document.createElement('canvas');
                  var canvas = canvasEl;
                  var context = canvas.getContext('2d');
                  canvas.height = viewport.height;
                  canvas.width = viewport.width;
                  var renderContext = {
                      canvasContext: context,
                      viewport: viewport
                  };
                  page.render(renderContext).then(function () {
                      var canvasWrapper = document.createElement('div');
                      canvasWrapper.appendChild(canvasEl);
                      currentPageNum++
                      pages[num - 1] = canvasWrapper
                      openIfDocumentReady()
                  })
              }

              function openIfDocumentReady() {
                  if(pagesCount === currentPageNum) {
                      openPrintable()
                  }
              }

              pdfjsLib.getDocument({url: file})
                  .then(function(pdf) {
                      pagesCount = pdf.numPages
                      for (let num = 1; num <= pdf.numPages; num++) {
                          pdf.getPage(num).then(function(page) {
                              renderPage(page, num)
                          })
                      }
                  })
          }

          $(".js-order-print").click(printHandler);
      },
      bindUpload: function(urls) {
        var uploadButtonHandler = function() {
          var order_id = $(this).data("order-id");
          $('.upload-external-report-file[data-order-id="'+order_id+'"]').click();
        };
        var uploadHandler = function() {
          var that = $(this),
            typeOfFile = that.data("object"),
            order_id = that.data("order-id"),
            dataUrl = that.data("url"),
            url;
          url = urls[typeOfFile];
          url += "?order_number=" + order_id;
          if (dataUrl) {
              url = dataUrl;
          }
          oscar.dashboard.orders.progressBar.show();
          var data = new FormData();
          data.append('external_report_pdf', $('.upload-external-report-file[data-order-id="'+order_id+'"]')[0].files[0]);
          $.ajax({
            method: 'post',
            url: url,
            data: data,
            processData: false,
            contentType: false,
            success: function(response) {
              o.messages.clear();
              o.messages.success(response.detail);
              $('.toggle-external-report[data-order-id="'+order_id+'"]').prop('checked', 'checked');
              $('.toggle-external-report[data-order-id="'+order_id+'"]').prop('disabled', false);
            },
            error: function(response) {
              oscar.dashboard.orders.progressBar.hide();
              o.messages.clear();
              var errorObj = JSON.parse(response.responseText);
              if (errorObj.detail) {
                o.messages.error(errorObj.detail);
                return;
              } else if (errorObj.external_report_pdf) {
                o.messages.error(errorObj.external_report_pdf);
                return;
              }
              o.messages.error("Something going wrong. Please, try again");
            },
            xhrFields: {
              onprogress: oscar.dashboard.orders.progressBar.onprogress
            }
          }).always(function() {
            setTimeout(function() {
              oscar.dashboard.orders.progressBar.hide();
            }, 1000);
          });
          var data = new FormData();
        };
        $(".js-order-upload").click(uploadButtonHandler);
        $(".upload-external-report-file").change(uploadHandler);
      },

      bindBatchAction: function() {
        o.radonmeters.batchOff = true;
        o.radonmeters.batchCounter = 0;
        var ids = [];
        var bulkApproveAction = function(id, counter) {
          var button = $('input.selected_order[value="' + id + '"]')
            .closest("tr")
            .find("button.approve-dosimeter");
          if (button && button.is(":visible")) {
            (function(btn) {
              setTimeout(function() {
                btn.click();
              }, 500 + 500 * counter);
            })(button);
            counter += 1;
            o.radonmeters.batchCounter += 1;
          }
        };
        var bulkSendAction = function(id, counter) {
          var button = $('input.selected_order[value="' + id + '"]')
            .closest("tr")
            .find("button.js-send-report");
          if (button && button.prop("disabled") == false) {
            (function(btn) {
              setTimeout(function() {
                btn.click();
              }, 500 + 500 * counter);
            })(button);
            counter += 1;
            o.radonmeters.batchCounter += 1;
          }
        };
        var bulkCreateShipmentAction = function(id, counter) {
          var button = $('input.selected_order[value="' + id + '"]')
            .closest("tr")
            .find("button.js-create-shipment");
          if (button && !!button.length) {
            (function(btn) {
              setTimeout(function() {
                btn.click();
              }, 500 + 500 * counter);
            })(button);
            counter += 1;
            o.radonmeters.batchCounter += 1;
          }
        };
        var actionHandler = function() {
          oscar.dashboard.orders.progressBar.show();
          o.radonmeters.batchOff = false;
          o.radonmeters.batchCounter = 0;
          console.log(o.radonmeters.batchOff);
          o.messages.clear();
          var that = $(this),
            type = that.data("type"),
            action = that.data("action");
          if (type === "bulk") {
            var counter = 0;
            console.log(ids);
            for (var i = 0; i < ids.length; i++) {
              switch (action) {
                case "approve":
                  bulkApproveAction(ids[i], counter);
                  break;
                case "send":
                  bulkSendAction(ids[i], counter);
                  break;
                case "create-shipment":
                  bulkCreateShipmentAction(ids[i], counter);
                  break;
                default:
                  break;
              }
            }
            setTimeout(function() {
              //o.radonmeters.batchOff = true;
              console.log(o.radonmeters.batchOff);
              //oscar.dashboard.orders.progressBar.hide();
            }, 500 + 500 * counter);
          }
        };
        $(".js-order-action").click(actionHandler);
        $(".selected_order").change(function() {
          if ($(this).prop("checked")) {
            ids.push($(this).val());
          } else {
            ids.splice(ids.indexOf($(this).val()), 1);
          }
        });
        $("th:first input").change(function() {
          if ($(this).prop("checked")) {
            $("input.selected_order").each(function() {
              ids.push($(this).val());
            });
          } else {
            ids = [];
          }
        });
      }
    },
    templatePreview: {
      conf: {
        base64Prefix: "data:image/png;base64,",
        $spinner: null,
        postUrl: ".",
        refreshDebounceTime: 400
      },
      renderErrors: function(errors) {
        $(".error-block").remove();
        var errHtml =
          '<span class="error-block"><i class="icon-exclamation-sign"></i> {{$}}</span>';
        for (name in errors) {
          if (!errors.hasOwnProperty(name)) continue;

          $('[name="' + name + '"]')
            .parent()
            .append($(errHtml.replace("{{$}}", errors[name][0])));
        }
      },
      togglePreview: function(isOpen) {
        var $editor_side = $(".editor-side"),
          $preview_side = $(".preview-side");

        $editor_side.toggleClass("col-md-6", isOpen);
        $preview_side.toggleClass("hidden", !isOpen);
      },
      handleUpdatePreview: function() {
        var that = this;
        that.conf.$spinner.removeClass("hidden");
        $(".error-block").remove();
        var params = {};

        for (var key in that.conf.dataFields) {
          if (!that.conf.dataFields.hasOwnProperty(key)) continue;
          params[key] = (
            !!that.conf.dataFields[key].val &&
            that.conf.dataFields[key] instanceof jQuery
            )
              ? that.conf.dataFields[key].val()
              : that.conf.dataFields[key];
        }

        $.ajax(that.conf.postUrl, {
          type: "post",
          cache: false,
          mimeType: "text/plain; charset=x-user-defined",
          data: params,
          success: function(res) {
            var image = new Image();
            image.src = that.conf.base64Prefix + base64Encode(res);
            image.style.width = "100%";
            $(".preview-image-wrapper")
              .empty()
              .append(image);
            that.togglePreview(true);
          },
          error: function(res) {
            that.togglePreview(false);
            var error = JSON.parse(res.responseText).errors;
            that.renderErrors(error);
          }
        }).done(function() {
          that.conf.$spinner.addClass("hidden");
        });
      },
      init: function(opt) {
        var that = this;
        var report = true
        that.conf.$spinner = $(".spinner");

        $.extend(that.conf, opt);

        let debouncedHandler = debounce(
          that.handleUpdatePreview.bind(that),
          that.conf.refreshDebounceTime
        );

        let debouncedHandlerEmail = debounce(
          displayDetails.bind(that),
          that.conf.refreshDebounceTime
        );

        $(".highlighted-editor textarea").each(function() {
          var editor = CodeMirror.fromTextArea(this, {
            lineNumbers: true,
            mode: "django",
            indentUnit: 2,
            indentWithTabs: true
          });
          editor.on("change", function() {
            editor.save();
            if (that.conf.autoRefreshField instanceof jQuery &&that.conf.autoRefreshField.prop("checked")) {
                if (report) {
                    debouncedHandler();
                } else {
                    debouncedHandlerEmail();
                }
            }
          });
        });
        $('#id_email_subject_template').keyup(function() {
            if (!report) {
                debouncedHandlerEmail();
            }
        })
        $('#is_autorefresh').change(function() {
            if($(this).is(":checked")) {
                report = false
            } else {
                report = true
            }
        });

        $(".close-preview").click(function(e) {
          e.preventDefault();
          that.togglePreview(false);
        });

        $('button[name="render_preview"]').click(function() {
          that.handleUpdatePreview();
        });

        function displayDetails() {
            var params = {};
            for (var key in that.conf.dataFields) {
                if (!that.conf.dataFields.hasOwnProperty(key)) continue;
                params[key] = (
                    !!that.conf.dataFields[key].val &&
                    that.conf.dataFields[key] instanceof jQuery
                )
                    ? that.conf.dataFields[key].val()
                    : that.conf.dataFields[key];
            }
            $.ajax(that.conf.postUrl, {
                type: "post",
                cache: false,
                mimeType: "text/plain; charset=x-user-defined",
                data: params,
                success: function(res) {
                    $(".error-block").remove();
                    $('#common-error').css('display', 'none')
                    const data = JSON.parse(res)
                    $('#show-order-details--subject')
                        .empty()
                        .append(data.data.subject);
                    $('#show-order-details--body')
                        .empty()
                        .append(data.data.body);
                    $('#show-order-details--html')
                        .empty()
                        .append(data.data.html);
                    $('.show-order-details').css('display', 'inline-block');
                },
                error: function(res) {
                    that.togglePreview(false);
                    var error = JSON.parse(res.responseText).errors;
                    if (error.__all__) {
                        $(".error-block").remove();
                        $('#common-error').css('display', 'block')
                        $('.common-error-alert-inner').text(error.__all__[0])
                    } else {
                        that.renderErrors(error);
                    }
                }
            }).done(function() {
                that.conf.$spinner.addClass("hidden");
            });
        }
         $('.display-details').click(displayDetails)
      }
    },
    user: {
      disableForm: false,
      updateInit: function(isDisable) {
        var u = o.dashboard.user;
        u.$editBtn = $(".js-edit-user");
        u.$cancel = $(".js-cancel");
        u.$update = $(".js-update-user");
        u.$form = $(".js-user-form");

        u.disableForm = isDisable;

        u.$form.find("input").prop("disabled", u.disableForm);

        u.$editBtn.click(function() {
          u.toggleForm(u);
        });

        u.$cancel.click(function() {
          u.toggleForm(u);
        });

        u.$form.submit(function(e) {
          if (u.disableForm) {
            e.preventDefault();
            return false;
          }
        });
      },
      toggleForm: function(u) {
        u.disableForm = !u.disableForm;
        u.$editBtn.toggleClass("hidden", !u.disableForm);
        u.$form.find("input").prop("disabled", u.disableForm);
        $([u.$cancel, u.$update]).toggleClass("hidden", u.disableForm);
      }
    },
    reordering: (function() {
      var options = {
          handle: ".btn-handle",
          submit_url: "#"
        },
        saveOrder = function(data) {
          // Get the csrf token, otherwise django will not accept the
          // POST request.
          var csrf = o.getCsrfToken();
          $.ajax({
            type: "POST",
            data: $.param(data),
            dataType: "json",
            url: options.submit_url,
            beforeSend: function(xhr, settings) {
              xhr.setRequestHeader("X-CSRFToken", csrf);
            }
          });
        },
        init = function(user_options) {
          options = $.extend(options, user_options);
          var group = $(options.wrapper).sortable({
            group: "serialization",
            containerSelector: "tbody",
            itemSelector: "tr",
            handle: options.handle,
            vertical: true,
            onDrop: function($item, container, _super) {
              var data = group.sortable("serialize");
              saveOrder(data);
              _super($item, container);
            },
            placeholder: '<tr class="placeholder"/>',
            serialize: function(parent, children, isContainer) {
              if (isContainer) {
                return children;
              } else {
                var parts = parent.attr("id").split("_");
                return { name: parts[0], value: parts[1] };
              }
            }
          });
        };

      return {
        init: init,
        saveOrder: saveOrder
      };
    })(),
    search: {
      init: function() {
        var searchForm = $(".orders_search"),
          searchLink = $(".pull_out"),
          doc = $("document");
        searchForm.each(function(index) {
          doc.css("height", doc.height());
        });
        searchLink.on("click", function() {
          searchForm
            .parent()
            .find(".pull-left")
            .toggleClass("no-float")
            .end()
            .end()
            .slideToggle("fast");
        });
      }
    },
    filereader: {
      init: function() {
        if (window.FileReader) {
          $('input[type="file"]').change(function(evt) {
            var that = $(this)
            var reader = new FileReader();
            var imgId = evt.target.id + "-image";
            reader.onload = (function() {
              return function(e) {
                // Add local file loader to update image files on change in
                // dashboard. This will provide a preview to the selected
                // image without uploading it. Upload only occures when
                // submitting the form.
                var imgDiv = $("#" + imgId);
                imgDiv.children("img").attr("src", e.target.result);
                //
                that.trigger( "onload:image", [{
                  target: e.target
                }]);
              };
            })();
            reader.readAsDataURL(evt.target.files[0]);
          });
        }
      }
    }
  };

  return o;

  function base64Encode(str) {
    var CHARS =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    var out = "",
      i = 0,
      len = str.length,
      c1,
      c2,
      c3;
    while (i < len) {
      c1 = str.charCodeAt(i++) & 0xff;
      if (i == len) {
        out += CHARS.charAt(c1 >> 2);
        out += CHARS.charAt((c1 & 0x3) << 4);
        out += "==";
        break;
      }
      c2 = str.charCodeAt(i++);
      if (i == len) {
        out += CHARS.charAt(c1 >> 2);
        out += CHARS.charAt(((c1 & 0x3) << 4) | ((c2 & 0xf0) >> 4));
        out += CHARS.charAt((c2 & 0xf) << 2);
        out += "=";
        break;
      }
      c3 = str.charCodeAt(i++);
      out += CHARS.charAt(c1 >> 2);
      out += CHARS.charAt(((c1 & 0x3) << 4) | ((c2 & 0xf0) >> 4));
      out += CHARS.charAt(((c2 & 0xf) << 2) | ((c3 & 0xc0) >> 6));
      out += CHARS.charAt(c3 & 0x3f);
    }
    return out;
  }

  function debounce(func, wait, immediate) {
    var timeout;
    return function() {
      var context = this,
        args = arguments;
      var later = function() {
        timeout = null;
        if (!immediate) func.apply(context, args);
      };
      var callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func.apply(context, args);
    };
  }
})(oscar || {}, jQuery);

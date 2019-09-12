(($, Vue) => {
    'use strict';

    Vue.component('date-picker', window.VueBootstrapDatetimePicker.default);

    Vue.component('select2', {
        props: ['options', 'value'],
        template: `<select>
                        <slot></slot>
                    </select>`,
        mounted: function() {
            var vm = this;
            $(this.$el)
                // init select2
                .select2({
                    data: this.options,
                    minimumResultsForSearch: -1,
                    width: '100%',
                    placeholder: this.$attrs.placeholder
                })
                .val(this.value)
                .trigger('change')
                // emit event on change.
                .on('change', function() {
                    vm.$emit('input', this.value);
                });
        },
        watch: {
            value: function(value) {
                // update value
                $(this.$el).val(value).trigger('change');
            },
            options: function(options) {
                // update options
                $(this.$el).empty().select2({ data: options,
                minimumResultsForSearch: -1,
                width: '100%',
                placeholder: this.$attrs.placeholder
            });
            }
        },
        destroyed: function() {
            $(this.$el).off().select2('destroy');
        }
    });

    let xhr;
    Vue.component('autocomplete', {
        model: {
            prop: 'value',
            event: 'change'
        },
        props: ['value', 'placeholder', 'disabled'],
        data() {
            return { inputVal: this.value }
        },
        template: `<input v-model="inputVal" :placeholder="placeholder" :disabled="disabled" class="form-control">`,
        mounted: function() {
            var vm = this;
            $(this.$el).autoComplete({
                minChars: 1,
                source: function(term, suggest) {
                    try { xhr.abort(); } catch(e){}
                    xhr = $.getJSON('/api/v1/locations/', { 
                        q: term 
                    }, function (data) { suggest(data.results) });
                },
                cache: false,
                renderItem: function (item, search){
                    search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                    var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
                    var html = '<div class="autocomplete-suggestion" data-id="'+ item.id +'" data-val="' + item.name + '">' + 
                        item.name.replace(re, "<b>$1</b>") + 
                    '</div>';
        
                    return html
                },
                onSelect(event, term, item) {
                    vm.inputVal = term
                }
            });
        },
        watch: {
            inputVal(val) {
                this.$emit('change', val);
            }
        },
        destroyed: function() {
            $(this.$el).destroy && $(this.$el).destroy();
        }
    });

    ////////////////////////////////////////////////////
    /// Product item(dosimeter)
    ////////////////////////////////////////////////////
    Vue.component('dosimeters',{
        template: '#dosimeters_product_row',

        props: ['item'],
        delimiters: ['<%', '%>'],
        data: function () {
            return {
                enableEdit: false,
                is_active: true,
                date_start: null,
                date_end: null,
                dispFormat: 'DD-MM-YYYY',
                initFormat: 'DD-MM-YYYY',
                floors: 5,

                datePickerConfigStart: {
                    format: 'DD-MM-YYYY',
                    dayViewHeaderFormat: 'MMMM YYYY',
                    useCurrent: true,
                    ignoreReadonly: true,
                },
                datePickerConfigEnd: {
                    format: 'DD-MM-YYYY',
                    dayViewHeaderFormat: 'MMMM YYYY',
                    ignoreReadonly: true,
                },
                selected: null,
                options: [],
                location: ''
            };
        },

        methods: {
            submitForm: function () {
                let formData = {
                    csrf_token: $('#order-list > input').val()
                };
                let that = this;

                $('#messages').empty();

                
                that.item.is_active = that.is_active;
                formData.is_active = that.is_active;

                if(that.date_start && that.date_start.isValid() && (that.item.measurement_start_date != that.date_start.format(that.initFormat))){
                    that.item.measurement_start_date = that.date_start.format(that.initFormat);
                    formData.measurement_start_date = that.date_start.format(that.initFormat);
                }

                if(that.date_end && that.date_end.isValid() && (that.item.measurement_end_date != that.date_end.format(that.initFormat))){
                    that.item.measurement_end_date = that.date_end.format(that.initFormat);
                    formData.measurement_end_date = that.date_end.format(that.initFormat);
                }

                if(!that.selected || (that.item.floor != that.selected)){
                    that.item.floor = that.selected;
                    formData.floor = that.selected;
                }


                if(that.item.location != that.location){
                    that.item.location = that.location || null;
                    formData.location = that.location || null;
                }


                /*if(that.isBlankFields()) {
                    return;
                }*/

                $.ajax(that.item.url, {
                    method: 'PATCH',
                    data: formData,
                    success: (data) => {
                        that.enableEdit = false;
                    },
                    error: () => {

                    }
                });

            },

            isBlankFields: function () {
                let errors = [];
                if(!this.date_start || !this.date_start.isValid()) {
                    errors.push($(this.$refs.start_date.$el).data('name'));
                }

                if(!this.date_end || !this.date_end.isValid()) {
                    errors.push($(this.$refs.end_date.$el).data('name'));
                }

                if(errors.length) {
                    _utils.renderMessages('danger', errors.join(', ').toLowerCase());
                    return true;
                }
            },
            handlerEdit: function () {
                if(this.item.status.value === 'on_store_side') {
                    return;
                }
                this.enableEdit = true;
            },
            location_id: function () {
                return 'location' + this.item.pk;
            },
            changeEndField: function(a,c) {
                $(this.$refs.end_date.$el).data("DateTimePicker").minDate(moment(this.date_start));

                if(moment(this.date_start).isSameOrAfter(this.date_end)) {
                    $(this.$refs.end_date.$el).data("DateTimePicker").clear();
                }

            }
        },

        created: function () {
            this.is_active = this.item.is_active;
            this.selected = _utils.isNumber(this.item.floor) ? this.item.floor : null;
            this.date_start = moment(this.item.measurement_start_date, this.initFormat);
            this.date_end = moment(this.item.measurement_end_date, this.initFormat);
            if(this.item.location) {
                this.location = this.item.location;
            }
        }
    });

     ////////////////////////////////////////////////////
    /// Product item(default)
    ////////////////////////////////////////////////////
    Vue.component('default-product',{
        template: '#default_product_row',

        props: ['item'],
        delimiters: ['<%', '%>'],
        data: function () {
            return {
                _data: ''
            };
        },

        created: function () {
            this._data = this.item;
        }
    });

    ////////////////////////////////////////////////////
    /// Order item
    ////////////////////////////////////////////////////
    Vue.component('order-item',{
        template: '#order-row',
        props: ['order'],
        delimiters: ['<%', '%>'],
        data: function () {
            return {
                defaultProducts: [],
                dosimeters: [],
                dosimetersListIsOpened: false,
                isFetch: false
            };
        },

        methods: {
            handlerToggleProductList: function () {
                if(this.defaultProducts.length === 0 && this.dosimeters.length === 0 ) {
                    return;
                }

                this.dosimetersListIsOpened = false;

                if(this.order.isOpened) {
                    this.$emit('close', this);
                    return;
                }

                this.$emit('open', this);
            },
            handlerToggleDosimeters: function () {
                this.dosimetersListIsOpened = !this.dosimetersListIsOpened;
            },
            checkForReport: function () {
                let that = this;
                that.isFetch = true;
                let url = that.order.generate_dosimeter_report_url;
                _utils.ajaxRequest(url, 'GET')
                .then(res => {
                    _utils.renderMessages('warning', res.detail);
                    that.isFetch = false;
                })
                .catch(res => {
                    window.location = url;
                    that.isFetch = false;
                });
            }
        },

        created: function () {
            this.defaultProducts = this.order.products.defaults;
            this.dosimeters = this.order.products.dosimeters;
        }
    });

    ////////////////////////////////////////////////////
    /// Main vm
    ////////////////////////////////////////////////////
    const orderList = new Vue({
        el: '#order-list',

        data: {
            showLoader: true,
            isEmpty: false,
            next_page: null,
            isDisabled: false,
            orders: [],
            orders_url: $('#order-list').data('url')
        },

        delimiters: ['<%', '%>'],
        methods:  {
            getData: function (url) {
                let that = this;
                let get_url = url ? url : that.orders_url;
                let to;

                this.showLoader = true;
                this.isDisabled = true;

                $.ajax(get_url, {
                    method: 'GET',
                    success: (data) => {
                        that.orders = that.orders.concat(data.results.map(function (item, indx) {
                            if(!url && indx === 0) {
                                item.isOpened = true;
                            } else {
                                item.isOpened = false;
                            }

                            return item;
                        }));

                        to = setTimeout(function() {
                            that.next_page = data.next;
                            that.showLoader = false;
                            that.isDisabled = false;
                            if(that.orders.length === 0) {
                                that.isEmpty = true;
                            }
                            clearTimeout(to);
                        }, 300);

                    }
                });

            },
            openOrder: function (emitter) {
                this.$children.forEach(function (item) {
                    item.order.isOpened = false;
                });
                emitter.order.isOpened = true;
            },
            closeOrder: function (emitter) {
                emitter.order.isOpened = false;
            },
            loadMore: function () {
                this.getData(this.next_page);
            }
        }

    });

    orderList.getData();

})(jQuery, window.Vue);
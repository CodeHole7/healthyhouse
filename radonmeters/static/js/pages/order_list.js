"use strict";!function(t,e){e.component("date-picker",window.VueBootstrapDatetimePicker.default),e.component("select2",{props:["options","value"],template:"<select>\n                        <slot></slot>\n                    </select>",mounted:function(){var e=this;t(this.$el).select2({data:this.options,minimumResultsForSearch:-1,width:"100%",placeholder:this.$attrs.placeholder}).val(this.value).trigger("change").on("change",function(){e.$emit("input",this.value)})},watch:{value:function(e){t(this.$el).val(e).trigger("change")},options:function(e){t(this.$el).empty().select2({data:e,minimumResultsForSearch:-1,width:"100%",placeholder:this.$attrs.placeholder})}},destroyed:function(){t(this.$el).off().select2("destroy")}});var i=void 0;e.component("autocomplete",{model:{prop:"value",event:"change"},props:["value","placeholder","disabled"],data:function(){return{inputVal:this.value}},template:'<input v-model="inputVal" :placeholder="placeholder" :disabled="disabled" class="form-control">',mounted:function(){var e=this;t(this.$el).autoComplete({minChars:1,source:function(e,a){try{i.abort()}catch(t){}i=t.getJSON("/api/v1/locations/",{q:e},function(t){a(t.results)})},cache:!1,renderItem:function(t,e){e=e.replace(/[-\/\\^$*+?.()|[\]{}]/g,"\\$&");var i=new RegExp("("+e.split(" ").join("|")+")","gi");return'<div class="autocomplete-suggestion" data-id="'+t.id+'" data-val="'+t.name+'">'+t.name.replace(i,"<b>$1</b>")+"</div>"},onSelect:function(t,i,a){e.inputVal=i}})},watch:{inputVal:function(t){this.$emit("change",t)}},destroyed:function(){t(this.$el).destroy&&t(this.$el).destroy()}}),e.component("dosimeters",{template:"#dosimeters_product_row",props:["item"],delimiters:["<%","%>"],data:function(){return{enableEdit:!1,is_active:!0,date_start:null,date_end:null,dispFormat:"DD-MM-YYYY",initFormat:"DD-MM-YYYY",floors:5,datePickerConfigStart:{format:"DD-MM-YYYY",dayViewHeaderFormat:"MMMM YYYY",useCurrent:!0,ignoreReadonly:!0},datePickerConfigEnd:{format:"DD-MM-YYYY",dayViewHeaderFormat:"MMMM YYYY",ignoreReadonly:!0},selected:null,options:[],location:""}},methods:{submitForm:function(){var e={csrf_token:t("#order-list > input").val()},i=this;t("#messages").empty(),i.item.is_active=i.is_active,e.is_active=i.is_active,i.date_start&&i.date_start.isValid()&&i.item.measurement_start_date!=i.date_start.format(i.initFormat)&&(i.item.measurement_start_date=i.date_start.format(i.initFormat),e.measurement_start_date=i.date_start.format(i.initFormat)),i.date_end&&i.date_end.isValid()&&i.item.measurement_end_date!=i.date_end.format(i.initFormat)&&(i.item.measurement_end_date=i.date_end.format(i.initFormat),e.measurement_end_date=i.date_end.format(i.initFormat)),i.selected&&i.item.floor==i.selected||(i.item.floor=i.selected,e.floor=i.selected),i.item.location!=i.location&&(i.item.location=i.location||null,e.location=i.location||null),t.ajax(i.item.url,{method:"PATCH",data:e,success:function(t){i.enableEdit=!1},error:function(){}})},isBlankFields:function(){var e=[];if(this.date_start&&this.date_start.isValid()||e.push(t(this.$refs.start_date.$el).data("name")),this.date_end&&this.date_end.isValid()||e.push(t(this.$refs.end_date.$el).data("name")),e.length)return _utils.renderMessages("danger",e.join(", ").toLowerCase()),!0},handlerEdit:function(){"on_store_side"!==this.item.status.value&&(this.enableEdit=!0)},location_id:function(){return"location"+this.item.pk},changeEndField:function(e,i){t(this.$refs.end_date.$el).data("DateTimePicker").minDate(moment(this.date_start)),moment(this.date_start).isSameOrAfter(this.date_end)&&t(this.$refs.end_date.$el).data("DateTimePicker").clear()}},created:function(){this.is_active=this.item.is_active,this.selected=_utils.isNumber(this.item.floor)?this.item.floor:null,this.date_start=moment(this.item.measurement_start_date,this.initFormat),this.date_end=moment(this.item.measurement_end_date,this.initFormat),this.item.location&&(this.location=this.item.location)}}),e.component("default-product",{template:"#default_product_row",props:["item"],delimiters:["<%","%>"],data:function(){return{_data:""}},created:function(){this._data=this.item}}),e.component("order-item",{template:"#order-row",props:["order"],delimiters:["<%","%>"],data:function(){return{defaultProducts:[],dosimeters:[],dosimetersListIsOpened:!1,isFetch:!1}},methods:{handlerToggleProductList:function(){0===this.defaultProducts.length&&0===this.dosimeters.length||(this.dosimetersListIsOpened=!1,this.order.isOpened?this.$emit("close",this):this.$emit("open",this))},handlerToggleDosimeters:function(){this.dosimetersListIsOpened=!this.dosimetersListIsOpened},checkForReport:function(){var t=this;t.isFetch=!0;var e=t.order.generate_dosimeter_report_url;_utils.ajaxRequest(e,"GET").then(function(e){_utils.renderMessages("warning",e.detail),t.isFetch=!1}).catch(function(i){window.location=e,t.isFetch=!1})}},created:function(){this.defaultProducts=this.order.products.defaults,this.dosimeters=this.order.products.dosimeters}}),new e({el:"#order-list",data:{showLoader:!0,isEmpty:!1,next_page:null,isDisabled:!1,orders:[],orders_url:t("#order-list").data("url")},delimiters:["<%","%>"],methods:{getData:function(e){var i=this,a=e||i.orders_url,s=void 0;this.showLoader=!0,this.isDisabled=!0,t.ajax(a,{method:"GET",success:function(t){i.orders=i.orders.concat(t.results.map(function(t,i){return t.isOpened=!e&&0===i,t})),s=setTimeout(function(){i.next_page=t.next,i.showLoader=!1,i.isDisabled=!1,0===i.orders.length&&(i.isEmpty=!0),clearTimeout(s)},300)}})},openOrder:function(t){this.$children.forEach(function(t){t.order.isOpened=!1}),t.order.isOpened=!0},closeOrder:function(t){t.order.isOpened=!1},loadMore:function(){this.getData(this.next_page)}}}).getData()}(jQuery,window.Vue);
//# sourceMappingURL=order_list.js.map
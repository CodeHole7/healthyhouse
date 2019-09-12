window.VueGoogleAutocomplete = {
    name: 'VueGoogleAutocomplete',

    template: `<input
        ref="autocomplete"
        type="text"
        :class="classname"
        :id="id"
        :placeholder="placeholder"
        v-model="autocompleteText"
        @focus="onFocus()"
        @blur="onBlur()"
        @change="onChange"
        @keypress="onKeyPress"
    />`,

    props: {
        location: ['location'],
        id: {
            type: String,
            required: true
        },

        classname: String,

        placeholder: {
            type: String,
            default: 'Start typing'
        },

        types: {
            type: String,
            default: '(cities)'
        },

        country: {
            type: [String, Array],
            default: null
        },

        enableGeolocation: {
            type: Boolean,
            default: false
        }
    },

    data: function data() {
        return {
            /**
             * The Autocomplete object.
             *
             * @type {Autocomplete}
             * @link https://developers.google.com/maps/documentation/javascript/reference#Autocomplete
             */
            autocomplete: null,

            /**
             * Autocomplete input text
             * @type {String}
             */
            autocompleteText: ''
        };
    },

    watch: {
        autocompleteText: function autocompleteText(newVal, oldVal) {
            this.$emit('inputChange', { newVal: newVal, oldVal: oldVal });
        }
    },

    mounted: function mounted() {
        var _this = this;

        var options = {};

        if (this.types) {
            options.types = [this.types];
        }

        if (this.country) {
            options.componentRestrictions = {
                country: this.country
            };
        }

        this.autocomplete = new google.maps.places.Autocomplete(document.getElementById(this.id), options);

        this.autocomplete.addListener('place_changed', function() {

            var place = _this.autocomplete.getPlace();

            if (!place.geometry) {
                // User entered the name of a Place that was not suggested and
                // pressed the Enter key, or the Place Details request failed.
                _this.$emit('no-results-found', place);
                return;
            }

            var addressComponents = {
                locality: 'long_name',
                administrative_area_level_1: 'short_name',
                country: 'long_name',
            };

            var returnData = {};

            if (place.address_components !== undefined) {
                // Get each component of the address from the place details
                for (var i = 0; i < place.address_components.length; i++) {
                    var addressType = place.address_components[i].types[0];

                    if (addressComponents[addressType]) {
                        var val = place.address_components[i][addressComponents[addressType]];
                        returnData[addressType] = val;
                    }
                }

                returnData['latitude'] = place.geometry.location.lat();
                returnData['longitude'] = place.geometry.location.lng();

                // return returnData object and PlaceResult object
                _this.$emit('placechanged', returnData, place, _this.id);

                // update autocompleteText then emit change event
                _this.autocompleteText = document.getElementById(_this.id).value;
                _this.onChange();
            }
        });
    },

    methods: {
        /**
         * When the input gets focus
         */
        onFocus: function onFocus() {
            this.geolocate();
            this.$emit('focus');
        },


        /**
         * When the input loses focus
         */
        onBlur: function onBlur() {
            this.$emit('blur');
        },


        /**
         * When the input got changed
         */
        onChange: function onChange() {
            this.$emit('change', this.autocompleteText);
        },


        /**
         * When a key gets pressed
         * @param  {Event} event A keypress event
         */
        onKeyPress: function onKeyPress(event) {
            this.$emit('keypress', event);
        },


        /**
         * Clear the input
         */
        clear: function clear() {
            this.autocompleteText = '';
        },


        /**
         * Focus the input
         */
        focus: function focus() {
            this.$refs.autocomplete.focus();
        },


        /**
         * Blur the input
         */
        blur: function blur() {
            this.$refs.autocomplete.blur();
        },


        /**
         * Update the value of the input
         * @param  {String} value
         */
        update: function update(value) {
            this.autocompleteText = value;
        },


        // Bias the autocomplete object to the user's geographical location,
        // as supplied by the browser's 'navigator.geolocation' object.
        geolocate: function geolocate() {
            var _this2 = this;

            if (this.enableGeolocation) {
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
                        _this2.autocomplete.setBounds(circle.getBounds());
                    });
                }
            }
        }
    }
};

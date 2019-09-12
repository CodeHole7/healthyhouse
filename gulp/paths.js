"use strict";

var _path = require("path");

var paths = {},
  filteredFiles = {},
  folders = {
    src: "./radonmeters/src_static",
    srcTpl: "./radonmeters/src_templates",
    dist: "./radonmeters/static", // change to static
    distTpl: "./radonmeters/templates",
    tasks: "./tasks",
    bower: "./bower_components"
  };

for (var pathName in folders) {
  if (folders.hasOwnProperty(pathName)) {
    paths[pathName] = (function(pathName) {
      return function() {
        var pathValue = folders[pathName];
        var funcArgs = Array.prototype.slice.call(arguments);
        var joinArgs = [pathValue].concat(funcArgs);

        return _path.join.apply(this, joinArgs);
      };
    })(pathName);
  }
}

// files which should be injected into base.html
filteredFiles = {
  scripts: [
    paths.src("js/components/csrf_ajax.js"),
    paths.src("js/common/main_navbar.js"),
    paths.src("js/common/slider.js"),
    paths.src("js/common/utils.js"),
    paths.src("js/common/footer.js"),
    paths.src("js/common/subnav.js"),
    paths.src("js/common/select2.js"),
    paths.src("js/common/add_to_basket.js"),
    paths.src("js/common/dropdown.js"),
    paths.src("js/common/cookie_accepting.js"),
    paths.src("js/common/language_switcher.js"),
    paths.src("js/components/popup.js"),
    paths.src("js/components/risk_inform.js"),
    paths.src("js/plugin/phone_mask.js")
  ],

  bower: [
    paths.bower("jquery/dist/jquery.min.js"),
    paths.bower("bootstrap-sass/assets/javascripts/bootstrap.min.js"),
    paths.bower("slick-carousel/slick/slick.min.js"),
    paths.bower("bLazy/blazy.min.js"),
    paths.bower("cookieconsent/build/cookieconsent.min.js"),
    paths.bower("stickyjs/stickyjs.js"),
    paths.bower("vue/dist/vue.min.js"),
    paths.bower("moment/min/moment-with-locales.min.js"),
    paths.bower("select2/dist/js/select2.full.min.js"),
    paths.bower("intl-tel-input/build/js/intlTelInput.min.js")
  ]
};

module.exports = {
  folders: folders,
  paths: paths,
  filteredFiles: filteredFiles
};

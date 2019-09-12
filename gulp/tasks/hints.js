'use strict';

var _gulp = require('gulp');
var _jshint  = require('gulp-jshint');
// ---
var paths = require('../paths.js').paths;


var hintScripts = function () {
    return _gulp.src([ paths.src('js/**/*.*'), '!' + paths.src('js/plugin/**/*.*') ])
        .pipe(_jshint('.jshintrc'))
        .pipe(_jshint.reporter(require('jshint-stylish')));
};


module.exports = {
    scripts:    hintScripts
};

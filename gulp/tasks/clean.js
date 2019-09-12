'use strict';

var _gulp = require('gulp');
var _clean = require('gulp-clean');
// ---
var paths = require('../paths.js').paths;


var clean = function clean (srcPathArray) {
    return function () {
        return _gulp.src( srcPathArray, { read: false } )
            .pipe(_clean({ force: true }));
    };
};


module.exports = {
    images:         clean([ paths.dist('images/**/*.*') ]),
    fonts:          clean([ paths.dist('fonts/**/*.*') ]),
    styles:         clean([ paths.dist('css/**/*.*') ]),
    scripts:        clean([ paths.dist('js/**/*.*') ]),
    bower:          clean([ paths.dist('bower/**/*.js') ])
};

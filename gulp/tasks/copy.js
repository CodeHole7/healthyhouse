'use strict';

var _gulp = require('gulp');
var _size = require('gulp-size');
// ---
var paths = require('../paths.js').paths;


var copy = function copy (srcPathArray, destPath) {
    return function () {
        return _gulp.src( srcPathArray )
            .pipe(_size())
            .pipe(_gulp.dest( destPath ));
    };
};


module.exports = {
    fonts:  copy([ paths.src('fonts/**/*.*') ], paths.dist('fonts'))
};

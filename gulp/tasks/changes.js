'use strict';

var _gulp = require('gulp');
var _size = require('gulp-size');
var _changed = require('gulp-changed');
// ---
var paths = require('../paths.js').paths;
var filteredFiles = require('../paths.js').filteredFiles;


var changesTemplates = function () {
    return _gulp.src([ paths.distTpl() ])
        .pipe(_changed( paths.distTpl() ))
        .pipe(_size({ title: '==> chnages:templates: ' }))
        .pipe(_gulp.dest( paths.distTpl() ));
};


var changesScripts = function () {
    return _gulp.src( filteredFiles.scripts )
        .pipe(_changed( paths.dist('js') ))
        .pipe(_size({ title: '==> chnages:scripts:change: ' }))
        .pipe(_gulp.dest( paths.dist('js') ));
};

var changesBower = function () {
    return _gulp.src( filteredFiles.bower )
        .pipe(_changed( paths.dist('bower') ))
        .pipe(_size({ title: '==> chnages:bower:change: ' }))
        .pipe(_gulp.dest( paths.dist('bower') ));
};


module.exports = {
    templates:      changesTemplates,
    scripts:        changesScripts,
    bower:          changesBower
};

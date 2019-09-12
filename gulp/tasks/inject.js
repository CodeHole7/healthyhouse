'use strict';

var _gulp = require('gulp');
var _inject = require('gulp-inject');
// ---
var paths = require('../paths.js').paths;
var filteredFiles = require('../paths.js').filteredFiles;
// ---
var helpers = require('../helpers.js');
var handlers = require('../handlers.js');
var _es = require('event-stream');

var inject = function () {
    var scriptsFilter = filteredFiles.scripts,
        bowerFilter = filteredFiles.bower,
        cssBundle = paths.dist('css/*.min.css');

    if (!helpers.isDev()) { // if build
        scriptsFilter = [ paths.dist('js/app.min.js') ];
        bowerFilter = [ paths.dist('bower/bower.min.js') ];
    }

    return _es.concat(
        _gulp.src([ paths.srcTpl('base/includes/scripts.html') ])
        .pipe(_inject( _gulp.src( bowerFilter, { read: false } ), {
            starttag: '<!-- inject:bower:{{ext}} -->',
            addRootSlash: false,
            addPrefix: '{% static \'',
            addSuffix: '\' %}',
            transform: handlers.injects.scripts
        }))
        .pipe(_inject( _gulp.src( scriptsFilter, { read: false } ), {
            starttag: '<!-- inject:scripts:{{ext}} -->',
            addRootSlash: false,
            addPrefix: '{% static \'',
            addSuffix: '\' %}',
            transform: handlers.injects.scripts
        }))
        .pipe(_gulp.dest( paths.distTpl('base/includes') )),

        _gulp.src([ paths.srcTpl('base/includes/styles.html') ])
            .pipe(_inject( _gulp.src( cssBundle, { read: false } ), {
                starttag: '<!-- inject:{{ext}} -->',
                addRootSlash: false,
                addPrefix: '{% static \'',
                addSuffix: '\' %}',
                transform: handlers.injects.styles
            }))
            .pipe(_gulp.dest( paths.distTpl('base/includes') ))
    );
};


module.exports = inject;

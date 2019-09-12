'use strict';

var _gulp = require('gulp');
var _size = require('gulp-size');
var _if = require('gulp-if');

var _rename = require('gulp-rename');
var _es = require('event-stream');

var _imagemin = require('gulp-imagemin');

var _sass = require('gulp-sass');
var _autoprefixer = require('gulp-autoprefixer');
var _sourcemaps = require('gulp-sourcemaps');
var _rev = require('gulp-rev');

var _concat  = require('gulp-concat');
var _uglify  = require('gulp-uglify');
var _stripDebug  = require('gulp-strip-debug');
// ---
var paths = require('../paths.js').paths;
var filteredFiles = require('../paths.js').filteredFiles;
var helpers = require('../helpers.js');
var handlers = require('../handlers.js');

const _babel = require('gulp-babel');

var gutil = require('gulp-util');

var processImages = function () {
    return _gulp.src([ paths.src('images/**/*.*') ])
        .pipe( _if(!helpers.isDev(), _imagemin({
                // setting interlaced to true. link: [ https://goo.gl/G7kt0S ]
                /*verbose: true,*/ // show in console optimization
                interlaced: true,
                progressive: true,
                optimizationLevel: 5
            })))
        .pipe(_size({ title: '==> process:images: ' }))
        .pipe(_gulp.dest( paths.dist('images') ));
};

var processStyles = function () {
    return _gulp.src([paths.src('scss/main.scss')])
        .pipe( _if(helpers.isDev(), _sourcemaps.init({largeFile: true})) )
            .pipe(_sass({
                    includePaths: [
                        './bower_components/'
                    ],
                    outputStyle: 'compressed'
                })).on('error', handlers.error('processing sass: '))
            .pipe(_autoprefixer({
                    browsers: ['last 5 versions'],
                    cascade: false,
                    remove: true,
                    supports: false
                })).on('error', handlers.error('processing sass: '))
            .pipe(_rename('main.min.css'))
            .pipe(_if(!helpers.isDev(), _rev()))
        .pipe( _if(helpers.isDev(), _sourcemaps.write('.')) )
        .pipe(_size({ title: '==> process:styles: ' }))
        .pipe(_gulp.dest(paths.dist('css')));
};

var processScripts = function () {
    return _es.concat(
        _gulp.src([ paths.src('js/**/*.*') ])
            .pipe( _if(!helpers.isDev(), _sourcemaps.init()) )
                .pipe( _if(!helpers.isDev(), _stripDebug()) )
                .pipe(_babel({
                    presets: ['env']
                }))
                .pipe( _if(!helpers.isDev(), _uglify()) )
                .on('error', function (err) { gutil.log(gutil.colors.red('[Error]'), err.toString()); })
            .pipe( _if(!helpers.isDev(), _sourcemaps.write('.')) )
            .pipe(_size({ title: '==> process:scripts: ' }))
            .pipe(_gulp.dest( paths.dist('js') )),

        _gulp.src( filteredFiles.scripts )
            .pipe( _if(!helpers.isDev(), _sourcemaps.init()) )
                .pipe( _if(!helpers.isDev(), _concat('app.min.js')) )
                .pipe( _if(!helpers.isDev(), _stripDebug()) )
                .pipe(_babel({
                    presets: ['env']
                }))
                .pipe( _if(!helpers.isDev(), _uglify()) )
                .on('error', function (err) { gutil.log(gutil.colors.red('[Error]'), err.toString()); })
            .pipe( _if(!helpers.isDev(), _sourcemaps.write('.')) )
            .pipe(_size({ title: '==> process:scripts:inject: ' }))
            .pipe(_gulp.dest( paths.dist('js') ))
    );
};

var processBower = function () {
    return _es.concat(
        _gulp.src([paths.bower('**') ])
            .pipe(_size({ title: '==> process:bower: ' }))
            .pipe(_gulp.dest( paths.dist('bower') )),

         _gulp.src( filteredFiles.bower )
            .pipe( _if(!helpers.isDev(), _sourcemaps.init()) )
            .pipe( _if(!helpers.isDev(), _concat('bower.min.js')) )
            .pipe( _if(!helpers.isDev(), _sourcemaps.write('.')) )
            .pipe(_size({ title: '==> process:bower:inject: ' }))
            .pipe(_gulp.dest( paths.dist('bower') ))
    );
};


module.exports = {
    images:         processImages,
    scripts:        processScripts,
    bower:          processBower,
    styles:         processStyles
};

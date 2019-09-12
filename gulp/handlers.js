'use strict';

var _gutil = require('gulp-util');
// ---
var helpers = require('./helpers.js');


var errorHandler = function (message) {
    return function (err) {
        _gutil.log(
            _gutil.colors.red(message), err.toString());

        this.emit('end');
    };
};

var changeHandler = function (e) {
    _gutil.log(
        _gutil.colors.blue(
            'File ' + e.path + ' was ' + e.type + ', running task ...'));
};

var deleteHandler = function (err, deletedFiles) {
    if (err) {
        errorHandler('deleteHandler')(err);
    }

    if (helpers.isDev()) {
        _gutil.log(
            _gutil.colors.yellow('Files deleted: ', deletedFiles.join(', ')));
    }
};

var logHandler = function (message) {
    _gutil.log(_gutil.colors.blue(message));
};

var injectTransformHandler = {
    styles: function (filePath) {
        var link_start = '<link rel="stylesheet" href="';
        var link_end = '" type="text/css">';
        var file_path = filePath.replace('/radonmeters/static/', '');
        return link_start + file_path + link_end;
    },
    scripts: function (filePath) {
        var script_start = '<script type="text/javascript" src="';
        var script_end = '"></script>';
        // for build task
        var file_path = filePath.replace('/radonmeters/static/', '');
        // for develop task
        var file_path = file_path.replace('/radonmeters/src_static/', '');
        var file_path = file_path.replace('/bower_components', 'bower');

        var file_path = file_path + '?t=' + ( (new Date()).getTime() );
        return script_start + file_path + script_end;
    }
};


module.exports = {
    error: errorHandler,
    change: errorHandler,
    delete: errorHandler,
    log: logHandler,
    injects: injectTransformHandler
};

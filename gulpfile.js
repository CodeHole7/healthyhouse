'use strict';

var _gulp = require('gulp');
var _bs = require('browser-sync');
var _pump = require('pump');
// ---
var paths = require('./gulp/paths.js').paths;
var filteredFiles = require('./gulp/paths.js').filteredFiles;
// ---
var clean = require('./gulp/tasks/clean.js');
var copy = require('./gulp/tasks/copy.js');
var proc = require('./gulp/tasks/process.js');
var changes = require('./gulp/tasks/changes.js');
var inject = require('./gulp/tasks/inject.js');
var hints = require('./gulp/tasks/hints.js');

var _log = require('./gulp/handlers.js').log;

//=============================================================================
// CLEAN:

var cleanSubTasksArray = [];
for (var taskName in clean) {
    if (!clean.hasOwnProperty(taskName)) continue;

    ;(function (taskName) {
        var cleanSubTaskName = 'clean:' + taskName;
        _gulp.task(cleanSubTaskName, clean[taskName]);
        cleanSubTasksArray.push(cleanSubTaskName);
    })(taskName);
}
_gulp.task('clean', cleanSubTasksArray);

//=============================================================================
// COPY:

var copySubTasksArray = [];
for (var taskName in copy) {
    if (!copy.hasOwnProperty(taskName)) continue;

    ;(function (taskName) {
        var copySubTaskName = 'copy:' + taskName;
        _gulp.task(copySubTaskName, [ 'clean:' + taskName ], copy[taskName]);
        copySubTasksArray.push(copySubTaskName);
    })(taskName);
}

_gulp.task('copy', copySubTasksArray);

//=============================================================================
// PROCESS:

var processSubTasksArray = [];
for (var taskName in proc) {
    if (!proc.hasOwnProperty(taskName)) continue;

    ;(function (taskName) {
        var processSubTaskName = 'process:' + taskName;
        _gulp.task(processSubTaskName, [ 'clean:' + taskName ], proc[taskName]);
        processSubTasksArray.push(processSubTaskName);
    })(taskName);
}

_gulp.task('process', processSubTasksArray);

//=============================================================================
// CHANGES:

var changesSubTasksArray = [];
for (var taskName in changes) {
    if (!changes.hasOwnProperty(taskName)) continue;

    ;(function (taskName) {
        var changesSubTaskName = 'changes:' + taskName;
        _gulp.task(changesSubTaskName, changes[taskName]); // hasn't any other dependencies
        changesSubTasksArray.push(changesSubTaskName);
    })(taskName);
}

_gulp.task('changes', changesSubTasksArray);

//=============================================================================
// INJECT:

_gulp.task('inject:build', [
    'process:bower',
    'process:scripts',
    'process:styles'
], inject);

_gulp.task('inject:develop', [
    'changes:bower',
    'changes:scripts',
    'process:styles'
], inject);

//=============================================================================
// WATCH:

_gulp.task('watch', function () {
    _gulp.watch( paths.src('fonts/**/*.*'), [ 'copy:fonts' ]);
    _gulp.watch( paths.src('images/**/*.*'), [ 'process:images' ]);
    _gulp.watch( paths.src('scss/**/*.*'), [ 'process:styles' ]);

    _gulp.watch( paths.src('js/**/*.*'), [ 'process:scripts' ]);
    _gulp.watch( paths.bower('**'), [ 'process:bower' ]);

    _gulp.watch( [
            paths.srcTpl('base/includes/scripts.html'),
            paths.srcTpl('base/includes/styles.html'),
            filteredFiles.scripts,      // 'changes:scripts'
            filteredFiles.bower         // 'changes:bower'
        ], [ 'inject:develop' ]);
});

//=============================================================================
// SERVE:

var reloadBS = function (done) {
    _bs.reload();
    done();
};

var reloadBSWithLog = function (text, e) {
    _log(text + ': ' + e);
    _bs.reload();
};

_gulp.task('watch:fonts', [ 'copy:fonts' ], reloadBS);

_gulp.task('watch:images', [ 'process:images' ], reloadBS);
_gulp.task('watch:styles', [ 'process:styles' ], reloadBS);
_gulp.task('watch:scripts', [ 'process:scripts' ], reloadBS);
_gulp.task('watch:bower', [ 'process:bower' ], reloadBS);

_gulp.task('watch:inject:develop', [ 'inject:develop' ], reloadBS);


_gulp.task('serve', function () {
    _bs.init({
        proxy: '127.0.0.1:8000', // ./manage.py runserver 127.0.0.1:8000
        host: "127.0.0.1",
        port: 8001
    });

    // ============ from _gulp.task 'watch' with few changes

    _gulp.watch( paths.src('fonts/**/*.*'), [ 'watch:fonts' ]);
    _gulp.watch( paths.src('images/**/*.*'), [ 'watch:images' ]);
    _gulp.watch( paths.src('scss/**/*.*'), [ 'watch:styles' ]);
    _gulp.watch( paths.src('js/**/*.*'), [ 'watch:scripts' ]);
    _gulp.watch( paths.bower('**'), [ 'watch:bower' ]);

    _bs.watch(paths.distTpl('*.*')).on('change', reloadBSWithLog.bind(null, 'Template dist changed'));
    _bs.watch(paths.srcTpl('*.*')).on('change', reloadBSWithLog.bind(null, 'Template dist changed'));

    _gulp.watch( [
            paths.srcTpl('base/includes/scripts.html'),
            paths.srcTpl('base/includes/styles.html'),
            filteredFiles.scripts,      // 'changes:scripts'
            filteredFiles.bower         // 'changes:bower'
        ], [ 'watch:inject:develop' ]);
});

//=============================================================================
// CODE QUALITY:

_gulp.task('hints:scripts', hints.scripts);

//=============================================================================
// COMMON:

_gulp.task('build', [ 'clean', 'copy', 'process', 'inject:build' ]);
_gulp.task('develop', [ 'clean', 'copy', 'process', 'inject:build' ]);

_gulp.task('develop:watch', [ 'watch' ]);
_gulp.task('develop:serve', [ 'serve' ]);

_gulp.task('default', [ 'develop' ]);

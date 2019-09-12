'use strict';

var isDev = function () {
    return process.env.NODE_ENV === 'develop';
};

var isArray = function (array) {
    return Object.prototype.toString.call(array).substring(8, 13) === 'Array';
};


module.exports = {
    isDev: isDev,
    isArray: isArray
};

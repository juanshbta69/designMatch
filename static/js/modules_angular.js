/**
 * Created by Lina8a on 15/02/2016.
 */

var app = angular.module('app_buscoayuda', []).config(function ($interpolateProvider) {

    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});
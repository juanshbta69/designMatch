/**
 * Created by Lina8a on 15/02/2016.
 */

app.controller('ctrl_base', function ($scope, $http, $rootScope) {
    $scope.logged = localStorage.getItem("buscoayuda-id");

    $scope.log_out = function () {
        localStorage.removeItem("buscoayuda-id");
        window.location.href = "/";
    }

    $scope.view_profile = function () {
        window.location.href = "/detalle/" + localStorage.getItem('buscoayuda-id') + "/";
    }

});



app.controller('ctrl_login', function ($scope, $http, $rootScope) {

    $scope.login = {};

    $scope.login = function () {

        $scope.post_login();
    }

    $scope.post_login = function () {

        $http({
            method: 'POST',
            url: '/post_login/',
            data: $scope.serialize($scope.login),
            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
        })
            .success(function (data, status) {
                localStorage.setItem("buscoayuda-id", data);
                window.location.href = "/";
            }).error(function (data, status) {
            window.location.href = "/register/";
        })
    };

    $scope.serialize = function (obj) {
        var str = [];
        for (var p in obj) {
            if (obj.hasOwnProperty(p)) {
                str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
            }
        }
        return str.join("&");
    };

});



var tspyControllers = angular.module('tspyControllers', []);

tspyControllers.controller('MessagesCtrl', ["$scope", "$http", function ($scope, $http) {
	$http.get("api/messages").success(function (data) {
		$scope.messages = data;
	});
}]);
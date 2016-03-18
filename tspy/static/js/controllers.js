var tspyControllers = angular.module('tspyControllers', []);

tspyControllers.controller('MessagesCtrl', ["$scope", "$http", function ($scope, $http) {
	function parseTargetmode(mode) {
		switch (mode) {
			case 1:
				return "CLIENT";
			case 2:
				return "CHANNEL";
			case 3:
				return "SERVER";
			default:
				return "UNKNOWN";
		}
	}
	function update() {
		console.log("update");
		$http.get("api/messages").success(function (data) {
			var messages = data.map(function (x) {
				return {
					date: x.date,
					sender: x.sender,
					targetmode: parseTargetmode(x.targetmode),
					target: x.target,
					msg: x.msg
				};
			});
			if (messages.length > 500)
				messages = messages.splice(0, 500);
			$scope.messages = messages;
			setTimeout(function () {
				if (shouldUpdate)
					update();
			}, 5000);
		});
	}
	var shouldUpdate = true;
	$scope.$on("$routeChangeStart", function () {
		shouldUpdate = false;
	})
	update();
}]);
tspyControllers.controller('NavbarCtrl', ["$location", "$scope", function ($location, $scope) {
	$scope.isActive = function (viewLocation) { 
		if (viewLocation == "/")
			return $location.path() == "" || $location.path() == "/";
		else
        	return $location.path().indexOf(viewLocation) == 0;
    };
}]);
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
				return "UNKNOWN (" + mode + ")";
		}
	}
	function update() {
		console.log("update");
		$http.get("api/inspect/messages?secret=" + localStorage.getItem("secret")).success(function (data) {
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
	});
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
tspyControllers.controller("QueueCtrl", ["$scope", "$http", function ($scope, $http) {
	function updateQueue() {
		var completedTasks = 0;
		$http.get("api/inspect/queue?secret=" + localStorage.getItem("secret")).success(function (data) {
			var commands = data.map(function (x) {
				return {
					id: x.id,
					command: x.command,
					header: x.header,
					extra: x.extra
				}
			});
			console.log(commands);
			$scope.queue = commands;
			completedTasks++;
			if (completedTasks == 2 && shouldUpdate)
				setTimeout(function () {
					updateQueue();
				}, 1000);
		});
		$http.get("api/inspect/queue/completed?secret=" + localStorage.getItem("secret")).success(function (data) {
			var commands = data.map(function (x) {
				return {
					id: x.id,
					command: x.command,
					header: x.header,
					extra: x.extra
				}
			});
			console.log(commands);
			$scope.completed_commands = commands;
			completedTasks++;
			if (completedTasks == 2 && shouldUpdate)
				setTimeout(function () {
					updateQueue();
				}, 1000);
		});
	}
	var shouldUpdate = true;
	$scope.$on("$routeChangeStart", function () {
		shouldUpdate = false;
	});
	$scope.submit = function () {
		console.log($.param($scope.formData));
		$http({
			method: "POST",
			url: "api/queue?secret=" + localStorage.getItem("secret"),
			data: $.param($scope.formData),
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }  
		}).success(function () {
			$scope.formData = {};
		});
	}
	$scope.removeFromQueue = function (id) {
		console.log($.param({id:id}))
		$http({
			method: "POST",
			url: "api/queue/delete?secret=" + localStorage.getItem("secret"),
			data: "id=" + id,
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }  
		})
	}
	$scope.applyPreset = function (preset) {
		switch (preset) {
			case "poke":
				$scope.formData = {
					command: "clientpoke clid=2 msg=template return_code=1:18",
					header: "?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 01 23",
					extra: ""
				}
				break;
			case "server_chat":
				$scope.formData = {
					command: "sendtextmessage targetmode=3 msg=template",
					header: "?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??",
					extra: ""
				}
		}
	}
	updateQueue();
}]);
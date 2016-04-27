var tspyApp = angular.module('tspyApp', [
  'ngRoute',
  "ngSanitize",
  'tspyControllers'
]);

var applySecret = function (url) {
	return url + "?secret=" + localStorage.getItem("secret");
}

tspyApp.config(['$routeProvider',
	function($routeProvider) {
		$routeProvider.
			when('/messages', {
				templateUrl: applySecret('partials/messages.html'),
				controller: 'MessagesCtrl'
			}).
			when('/queue', {
				templateUrl: applySecret('partials/queue.html'),
				controller: 'QueueCtrl'
			}).
			when('/errors', {
				templateUrl: applySecret('partials/errors.html'),
				controller: 'ErrorsCtrl'
			}).
			when('/', {
				templateUrl: applySecret('partials/index.html'),
			}).
			otherwise({
				templateUrl: applySecret('partials/index.html')
			})
}]);
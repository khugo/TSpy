var tspyApp = angular.module('tspyApp', [
  'ngRoute',
  "ngSanitize",
  'tspyControllers'
]);

tspyApp.config(['$routeProvider',
	function($routeProvider) {
		$routeProvider.
			when('/messages', {
				templateUrl: 'partials/messages.html',
				controller: 'MessagesCtrl'
			}).
			when('/queue', {
				templateUrl: 'partials/queue.html',
				controller: 'QueueCtrl'
			}).
			when('/errors', {
				templateUrl: 'partials/errors.html',
				controller: 'ErrorsCtrl'
			}).
			when('/', {
				templateUrl: 'partials/index.html',
			}).
			otherwise({
				templateUrl: 'partials/index.html'
			})
}]);
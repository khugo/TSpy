var tspyApp = angular.module('tspyApp', [
  'ngRoute',
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
			when('/', {
				templateUrl: 'partials/index.html'
			}).
			otherwise({
				templateUrl: 'partials/index.html'
			})
}]);
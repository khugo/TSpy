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
			otherwise({
				templateUrl: 'partials/index.html'
			})
}]);
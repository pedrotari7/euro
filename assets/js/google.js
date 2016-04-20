
function onSuccess(googleUser) {
	console.log('Logged in as: ' + googleUser.getBasicProfile().getName());
  // The ID token you need to pass to your backend:
	var id_token = googleUser.getAuthResponse().id_token;
	console.log("ID Token: " + id_token);
	window.location.replace("/scripts/login.py?&token="+id_token);

}

function onFailure(error) {
  console.log(error);
}

function renderButton() {
	gapi.signin2.render('my-signin2', {
	'scope': 'profile email',
	'width': 240,
	'height': 50,
	'longtitle': true,
	'theme': 'dark',
	'onsuccess': onSuccess,
	'onfailure': onFailure
	});
}

function signOut() {
	var auth2 = gapi.auth2.getAuthInstance();
	auth2.signOut().then(function () {
	  console.log('User signed out.');
	  window.location = "http://www.euro16.win";
	});
}

function onLoad() {
  gapi.load('auth2', function() {
    gapi.auth2.init();
  });
}

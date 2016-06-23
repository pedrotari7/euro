
var remain = document.getElementById('remain');
console.log(remain);

function startTimer(duration, display) {
    var timer = duration, hours, minutes, seconds;
    setInterval(function () {

    	hours = parseInt(timer / 3600, 10);

        minutes = parseInt(timer / 60 - hours*60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.innerText = hours + ":" + minutes + ":" + seconds;

        if (--timer < 0) {
            location.reload();
        }
    }, 1000);
}

window.onload = function () {
	var start = remain.innerText;
	console.log(start);

	if (start.indexOf(":") > -1){
		
		var s = start.split(':');

		var total = parseInt(s[2],10);
		total += 60*parseInt(s[1],10);
		total += 3600*parseInt(s[0],10);

    	display = document.querySelector('#remain');
    	startTimer(total, display);
	}
};
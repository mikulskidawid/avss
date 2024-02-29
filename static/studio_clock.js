function getServerTime() {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
      document.getElementById("studio_clock").innerHTML = this.responseText;
      }
    xhttp.open("GET", "/requests/servertime", true);
    xhttp.send();
}

setInterval(getServerTime, 1000);
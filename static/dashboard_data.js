function getServerTime() {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        document.getElementById("server-time").innerHTML = this.responseText;
    }
    xhttp.open("GET", "/requests/servertime", true);
    xhttp.send();
}

function getSysInfo() {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        const data = JSON.parse(this.responseText);
        document.getElementById("system").innerHTML = data.system;
        document.getElementById("cpu").innerHTML = data.cpu;


        var cpu_used = document.getElementById("cpu-percent");
        cpu_used.innerHTML = data.cpu_percent+'%';
        cpu_used.style.width = data.cpu_percent+'%'

        document.getElementById("boot-time").innerHTML = data.boot_time;
    }
    xhttp.open("GET", "/requests/sysinfo", true);
    xhttp.send();
}

function getMemInfo() {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        const data = JSON.parse(this.responseText);
        document.getElementById("mem-total").innerHTML = data.total;

        var mem_used = document.getElementById("mem-used");
        var mem_used_percent = data.percent;
        var mem_free_percent = 100 - mem_used_percent;
        mem_used.innerHTML = data.used + ' ('+ mem_used_percent + '%)';
        mem_used.style.width = mem_used_percent;

        var mem_available = document.getElementById("mem-available");
        mem_available.innerHTML = data.available + ' ('+ mem_free_percent + '%)';
        mem_available.style.width = mem_free_percent;
    }
    xhttp.open("GET", "/requests/meminfo", true);
    xhttp.send();
}

function getDiscInfo() {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        const data = JSON.parse(this.responseText);
        var disc_used_per = parseFloat(data.used) / parseFloat(data.total) * 100;
        var disc_free_per = parseFloat(data.total-data.used) / parseFloat(data.total) * 100;
        document.getElementById("disc-total").innerHTML = data.total+'GB';

        var disc_used = document.getElementById("disc-used")
        disc_used.innerHTML = data.used+' GB ('+disc_used_per.toFixed(1)+'%)';
        disc_used.style.width = disc_used_per+'%';

        var disc_free = document.getElementById("disc-free");
        disc_free.innerHTML = data.free+' GB ('+disc_free_per.toFixed(1)+'%)';
        disc_free.style.width = disc_free_per+'%';

        document.getElementById("disc-filesystem").innerHTML = data.filesystem;
        document.getElementById("disc-mount").innerHTML = data.mount;

    }
    xhttp.open("GET", "/requests/discinfo", true);
    xhttp.send();
}

getServerTime();
getSysInfo();
getMemInfo();
getDiscInfo();

setInterval(getServerTime,1000);
setInterval(getSysInfo, 2000);
setInterval(getMemInfo, 2000);
setInterval(getDiscInfo, 4000);

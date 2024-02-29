let id = 0;

function nowPlayingText() {
    const xhttp = new XMLHttpRequest();

    xhttp.onload = function() {
        const data = JSON.parse(this.responseText);
        let groupType = parseInt(data.group_type);
        let nowPlaying = '';
        if(groupType==1) {
            nowPlaying = data.group_name + ', S'+data.video_season+'E'+data.video_episode+' "'+data.video_name+'"';
        }
        else{
            nowPlaying = data.video_name;
        }
        document.getElementById("now_playing").innerHTML = nowPlaying;
    }
    xhttp.open("GET", "/requests/playinfo", true);
    xhttp.send();
}

function getPlaylistID() {
    var xhttp = new XMLHttpRequest();
    var url = '/requests/playlist_id';
    xhttp.open('GET', url, true);
  
    xhttp.onreadystatechange = function () {
      if (xhttp.readyState === 4) {
        if (xhttp.status === 200) {
          id = parseInt(xhttp.responseText);
        }
      }
    };

    xhttp.send();
}

function setScroll(){
    let container = document.querySelector("#main-container");
    let items = document.getElementsByName('scheduleItem');
    let focus = document.querySelector('.schedule-item-highlight');
    focus.scrollIntoView();
    let height = parseInt(items[0].offsetHeight);
    //container.scrollTop = (height+10) * id;
}

function getSchedule() {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        const scheduleList = JSON.parse(this.responseText);
        let scheduleContainer = document.getElementById("schedule-container");
        scheduleContainer.innerHTML = '';

        scheduleList.forEach((item, index) => {
            const listItem = document.createElement('div');
            listItem.setAttribute("name", "scheduleItem");
            if(id==index) {
                listItem.classList.add('schedule-item-highlight');
            }
            else {
                listItem.classList.add('schedule-item');
            }

            let p1 = '<p><i class="fa fa-clock-o" aria-hidden="true"></i> '+item.video_time+' <i class="fa fa-calendar" aria-hidden="true"></i> '+item.video_date+'</p>';
            let p2 = '';
            if(item.group_type==1){
                p2 = '<p>'+item.group_name + ', S'+item.video_season+'E'+item.video_episode+' "'+item.video_name+'"</p>';
            }
            else {
                p2 = '<p>'+item.video_name +'</p>';
            }       
            listItem.innerHTML = p1+p2;
            scheduleContainer.appendChild(listItem);
        });
    }
    xhttp.open("GET", "/requests/daily_playlist", true);
    xhttp.send();
}

getSchedule();

setInterval(getPlaylistID, 100);
setInterval(nowPlayingText, 1000);
setInterval(getSchedule, 2000);
setInterval(setScroll, 1000);
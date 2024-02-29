//horizontal 
const leftPane = document.querySelector(".left");
const rightPane = document.querySelector(".right");
const gutter_horiz = document.querySelector(".gutter-horiz");

function updateHorizGutter(){
    const scheduleContainer = document.getElementById('schedule-container');
    const gutHor = document.getElementsByClassName("gutter-horiz");
    const topBar = document.getElementsByClassName("top-bar");
    let newHeight = parseInt(scheduleContainer.offsetHeight)+parseInt(topBar[0].offsetHeight);
    if(newHeight>860) gutHor[0].style.height = newHeight+'px';
  }

function horizontalResize(e) {

    window.addEventListener('mousemove', mousemove);
    window.addEventListener('mouseup', mouseup);
    
    let prevX = e.x;
    const leftPanel = leftPane.getBoundingClientRect();
    
    
    function mousemove(e) {
        let newX = prevX - e.x;
        leftPane.style.width = leftPanel.width - newX + "px";
    }
    
    function mouseup() {
        window.removeEventListener('mousemove', mousemove);
        window.removeEventListener('mouseup', mouseup);
        
    }

}


gutter_horiz.addEventListener('mousedown', horizontalResize);
setInterval(updateHorizGutter, 200);
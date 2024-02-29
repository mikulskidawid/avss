//horizontal 
const leftPane = document.querySelector(".left");
const rightPane = document.querySelector(".right");
const gutter_horiz = document.querySelector(".gutter-horiz");


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
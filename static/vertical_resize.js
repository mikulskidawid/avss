//vertical
const topPane = document.querySelector(".top");
const bottomPane = document.querySelector(".bottom");
const gutter_vert = document.querySelector(".gutter-vert");

function verticalResize(e) {

    window.addEventListener('mousemove', mousemove);
    window.addEventListener('mouseup', mouseup);
    
    let prevY = e.y;
    const bottomPanel = bottomPane.getBoundingClientRect();
    const topPanel = topPane.getBoundingClientRect();
    
    function mousemove(e) {
        let newY = prevY - e.y;
        if(bottomPane.offsetHeight>244){
            //bottomPane.style.height = bottomPanel.height + newY + "px";
            topPane.style.height = topPanel.height - newY + "px";
        }
        if(topPane.offsetHeight>240){
            bottomPane.style.height = bottomPanel.height + newY + "px";
            //topPane.style.height = topPanel.height - newY + "px";
        }
        
    }
    
    function mouseup() {
        window.removeEventListener('mousemove', mousemove);
        window.removeEventListener('mouseup', mouseup);
        
    }

}

gutter_vert.addEventListener('mousedown', verticalResize);
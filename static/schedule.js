// Object list
let scheduleList = [[],[],[],[],[],[],[]];
let fullSchedule = [];
let day = 0;

document.getElementById('schedule_form').addEventListener('submit', function(event) {
  scheduleList.forEach((scheduleDay, index) => {
    scheduleDay.forEach((item, index) => {
      let newItem = {
        itemDay: item.itemDay,
        itemType: item.itemType,
        itemID: item.itemID,
        itemMode: item.itemMode,
        itemTime: item.itemTime
      };
      fullSchedule.push(newItem);
    });
  });
  var scheduleListJSON = JSON.stringify(fullSchedule);
  document.getElementById('schedule_list').value = scheduleListJSON;
});

// Checks string time format
function checkTimeFormat(input) {

  var regex = /^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$/;

  if (regex.test(input)) {
    return true;
  } else {
    return false;
  }
}

// Time to seconds
function timeToSeconds(time) {
  var [hours, minutes, seconds] = time.split(":").map(Number);
  return hours * 3600 + minutes * 60 + seconds;
}

// Number of seconds to "hh:mm:ss" format string
function secondsToTime(seconds) {
  var hours = Math.floor(seconds / 3600);
  var secondsRest = seconds % 3600;
  var minutes = Math.floor(secondsRest / 60);
  var sec = secondsRest % 60;

  return (
      hours.toString().padStart(2, '0') + ":" +
      minutes.toString().padStart(2, '0') + ":" +
      sec.toString().padStart(2, '0')
  );
}

function sumTime(time1, time2) {

    var secondsSum = timeToSeconds(time1) + timeToSeconds(time2);

    return secondsToTime(secondsSum);
}

// Add new item to the schedule
function addScheduleItem(itemID, itemName, itemType, itemMode, itemLength) {
  const newItem = {
    itemID: itemID,
    itemName: itemName,
    itemType: itemType,
    itemMode: itemMode,
    itemLength: itemLength,
    itemTime: '00:00:00',
    useCustomTime: 0,
    itemDay: day
  };

  // Time calculations
  if (scheduleList[day].length > 0) {
    const lastItem = scheduleList[day][scheduleList[day].length - 1];
    newItem.itemTime = sumTime(lastItem.itemTime, lastItem.itemLength);
  }

  scheduleList[day].push(newItem);
  let index = scheduleList[day].length-1;
  let sumtime = sumTime(scheduleList[day][index].itemTime, scheduleList[day][index].itemLength);
  if(timeToSeconds(sumtime)>=60*60*24){
    scheduleList[day].splice(index, 1);
  }
  updateSchedule();
}

// Remove item from schedule
function removeScheduleItem(index) {
  scheduleList[day].splice(index, 1);
  updateSchedule();
}

// Move item up on the list
function moveUp(index) {
  if (index > 0) {
    const temp = scheduleList[day][index - 1];
    scheduleList[day][index - 1] = scheduleList[day][index];
    scheduleList[day][index] = temp;

    scheduleList[day][index - 1].useCustomTime = 0;
    scheduleList[day][index].useCustomTime = 0;

    updateSchedule();
  }
}

// Move item down on the list
function moveDown(index) {
  if (index < scheduleList[day].length - 1) {
    const temp = scheduleList[day][index + 1];
    scheduleList[day][index + 1] = scheduleList[day][index];
    scheduleList[day][index] = temp;

    scheduleList[day][index - 1].useCustomTime = 0;
    scheduleList[day][index].useCustomTime = 0;

    updateSchedule();
  }
}

function updateTime(index){
  scheduleList[day][index].useCustomTime = 1;
  customTime = document.getElementById('cus_time'+index).value;
  if(checkTimeFormat(customTime)) {
    let sumtime = sumTime(scheduleList[day][index].itemTime, scheduleList[day][index].itemLength);
    if(timeToSeconds(sumtime)<60*60*24){
      console.log('ups');
      console.log(timeToSeconds(sumtime));
      scheduleList[day][index].itemTime = customTime;
    }
    else document.getElementById('cus_time'+index).value = scheduleList[day][index].itemTime;
  }
  else document.getElementById('cus_time'+index).value = scheduleList[day][index].itemTime;
  updateSchedule();
  updateSchedule();
}

function updateMode(index){
  let select = document.getElementById('itemSelect'+index);
  scheduleList[day][index].itemMode = select.value;
}

function sortSchedule(){
  scheduleList[day].sort((a, b) => timeToSeconds(a.itemTime) - timeToSeconds(b.itemTime));
  scheduleList[day].forEach((item, index) => {
    if(index==0){
      item.itemTime='00:00:00';
    }
    else if(index>0){
      const lastItem = scheduleList[day][index - 1];
      item.itemTime = sumTime(lastItem.itemTime, lastItem.itemLength);
    }
  });
}

// Update schedule view
function updateSchedule() {
  const scheduleContainer = document.getElementById('schedule-container');
  scheduleContainer.innerHTML = '';

  scheduleList[day].forEach((item, index) => {

    // time update

    if(index==0){
      item.itemTime='00:00:00';
    }
    else if(index>0){
      if(item.useCustomTime==0){
        const lastItem = scheduleList[day][index - 1];
        item.itemTime = sumTime(lastItem.itemTime, lastItem.itemLength);
      }
      if(item.useCustomTime==1){
        const lastItem = scheduleList[day][index - 1];
        if(timeToSeconds(sumTime(lastItem.itemTime, lastItem.itemLength))>=timeToSeconds(item.itemTime)) {
          sortSchedule();
        }
        else{
          scheduleList[day].sort((a, b) => timeToSeconds(a.itemTime) - timeToSeconds(b.itemTime));
        }
      }
    }

    const listItem = document.createElement('div');
    listItem.classList.add('schedule-item');

    const itemInfo = document.createElement('p');
    itemInfo.innerHTML = `<b>${item.itemTime}</b>, Name: ${item.itemName}, Max Duration: ${item.itemLength}`;
    listItem.appendChild(itemInfo);

    if(item.itemType==0){
      const modeInput = document.createElement('select');
      modeInput.id = 'itemSelect'+index;
      let option1 = '<option value=1>Auto Increment</option>';
      if(item.itemMode==1) option1 = '<option value=1 selected>Auto Increment</option>';
      let option2 = '<option value=2>Random Shuffle</option>';
      if(item.itemMode==2) option2 = '<option value=2 selected>Random Shuffle</option>';
      modeInput.innerHTML += option1;
      modeInput.innerHTML += option2;
      modeInput.addEventListener('change', () => updateMode(index));
      listItem.appendChild(modeInput);
    }

    const timeUpdateInput = document.createElement('input');
    timeUpdateInput.type='text';
    timeUpdateInput.value=item.itemTime;
    timeUpdateInput.id='cus_time'+index;
    listItem.appendChild(timeUpdateInput);

    const timeUpdateBtn = document.createElement('button');
    timeUpdateBtn.innerHTML = '<i class="fa fa-pencil-square-o" aria-hidden="true"></i> Update Time';
    timeUpdateBtn.addEventListener('click', () => updateTime(index));
    listItem.appendChild(timeUpdateBtn);

    // Item btns

    const ScheduleBtnBar = document.createElement('div');
    ScheduleBtnBar.className="schedule-btn-bar";

    const upButton = document.createElement('button');
    upButton.innerHTML = '<i class="fa fa-chevron-up" aria-hidden="true"></i>';
    upButton.addEventListener('click', () => moveUp(index));
    ScheduleBtnBar.appendChild(upButton);

    const downButton = document.createElement('button');
    downButton.innerHTML = '<i class="fa fa-chevron-down" aria-hidden="true"></i>';
    downButton.addEventListener('click', () => moveDown(index));
    ScheduleBtnBar.appendChild(downButton);

    const removeButton = document.createElement('button');
    removeButton.innerHTML = '<i class="fa fa-trash" aria-hidden="true"></i>';
    removeButton.classList.add('remove-btn');
    removeButton.addEventListener('click', () => removeScheduleItem(index));
    ScheduleBtnBar.appendChild(removeButton);

    listItem.appendChild(ScheduleBtnBar);

    scheduleContainer.appendChild(listItem);
  });

}

function changeDay(newDay){
  day = newDay;
  updateSchedule();
  for(let btnID=0; btnID<7; btnID++){
    if(btnID==day) document.getElementById('day'+btnID).className='top-bar-active';
    else {
      document.getElementById('day'+btnID).className='';
    }
  }
}

function resetDay(){
  scheduleList[day] = [];
  updateSchedule();
}

function cloneDay(){
  tempSchedule = scheduleList[day];
  scheduleList.forEach((item, index) => {
    scheduleList[index]=tempSchedule;
  });
  updateSchedule();
}

function generateDay(){
  groupBtns = document.getElementsByName('groupBtn');
  groups = []
  groupBtns.forEach((item, index) => {
    groupValues = item.value.split(',');
    groups.push(groupValues);
  });
  resetDay();
  let curTime = 0;
  while(curTime<60*60*24){
    function shuffle(array) {
      let currentIndex = array.length,  randomIndex;
    
      // While there remain elements to shuffle.
      while (currentIndex > 0) {
    
        // Pick a remaining element.
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;
    
        // And swap it with the current element.
        [array[currentIndex], array[randomIndex]] = [
          array[randomIndex], array[currentIndex]];
      }
    
      return array;
    }
    groups = shuffle(groups);
    console.log(groups);
    addScheduleItem(parseInt(groups[0][0]), groups[0][1], parseInt(groups[0][2]), parseInt(groups[0][3]), groups[0][4]);
    curTime+=timeToSeconds(groups[0][4]);
  }
  updateSchedule();
}
const $checkOutTime = document.querySelector('#checkoutTime');
const $checkInTime = document.querySelector('#checkinTime');

const $checkInDate = document.querySelector("#checkinDate");
const $checkOutDate = document.querySelector("#checkoutDate");

//USSING MOMENT        

const sahii =new Date();

// const time = moment(sahii).format("hh:mm")
const time = moment(sahii).format("HH:mm")

const date = moment(sahii).format("YYYY-MM-DD")

// -------------------------------CHECKIN-----------------------------

$checkInTime.value = time;  //setting checkin time
$checkInDate.value =date ;    //setting the checkin time default value to today
$checkInTime.setAttribute("min","07:00"); 
$checkInTime.setAttribute("max","18:00"); //can be used to set the earlist timme (read more MDN docs)
// ----------------------------CHECK IN------------------------

// --------------------checkout------------------------


// const afterHr= moment(sahii).add(1, 'h').format("hh:mm"); --12hrs
const afterHr= moment(sahii).add(5,"m").format("HH:mm");   //--24hrs
console.log({sahii,afterHr})

$checkOutTime.value = afterHr;
$checkOutTime.setAttribute("min",`${afterHr}`);
$checkOutTime.setAttribute("max", "19:00");

$checkOutDate.value = date;
$checkOutDate.setAttribute("min",`${date}`);



// console.log(afterHr)

// -----------------------checkout---------------------

var x = document.getElementById("checkinTime");
var y = document.getElementById("checkoutTime");
var price = document.getElementById("amount");




function calculateTimeDifference() {
    var checkInTime = new Date("01/01/1900 " + x.value);
    var checkOutTime = new Date("01/01/1900 " + y.value);
    var timeDifference = (checkOutTime - checkInTime) / 1000 / 60; // in minutes
    var hours = Math.floor(timeDifference / 60);
    var minutes = Math.round(timeDifference % 60);
    price.value= (price.value *  timeDifference) / 60;
    console.log(timeDifference)
  }
  

  
const checkinInput = document.getElementById("checkinTime");
const checkoutInput = document.getElementById("checkoutTime");
const amountInput = document.getElementById("amount");

function calculateAmount() {
  const checkinDate = new Date(checkinInput.value);
  const checkoutDate = new Date(checkoutInput.value);

  const durationMs = checkoutDate.getTime() - checkinDate.getTime();
  const durationHours = durationMs / (1000 * 60 * 60); // convert to hours
  console.log(typeof(durationHours))
  // update amount value with 2 decimal places
  var amount=amountInput.value * durationHours
  console.log(amount)
  if (durationHours > 0){
    amountInput.value=amount;
  }
}

checkinInput.addEventListener("change", calculateAmount);
checkoutInput.addEventListener("change", calculateAmount);
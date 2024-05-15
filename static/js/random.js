function generateRandomNumber() {
    // Generate a 5-digit random number
    var randomNumber = Math.floor(10000 + Math.random() * 90000);

    // Update the value of the 'cid' input with the generated random number
    document.getElementById("cid").value = randomNumber;
}


var time = document.getElementById('ctm')
time.value = Date.now()
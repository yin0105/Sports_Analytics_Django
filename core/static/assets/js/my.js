function add_info() {
    document.getElementById("settings_way").value = "add";
    settings_form.submit();
}

function reset_calc() {
    document.getElementById("data").value = "";
    calc_form.submit();
}


function kellyBet(form) {
    // Convert Input Variables to Numeric Values
    PROB = eval(form.PROB0.value); // Probability - Enter your odds of winning, say, '.5' for a coin flip, or '.1' for one number out of 10.
    ODDS = eval(form.ODDS1.value); // Odds - Enter your net odds received, say '2' for 2 to 1 odds.
    BANK = eval(form.BANK2.value); // Bankroll - Enter the amount of money you have to bet. (Dollars)
    HK = eval(form.HK3.value); // Adjusted Kelly - Enter Your 'Kelly Adjustment' to divide.  '1' for full, '.5' for Half-Kelly, '.25' for Quarter-Kelly, etc.

    // Calculate values
    KC = ((PROB*(ODDS+1)-1)/ODDS)*HK; // Kelly Criterion (Adjusted)
    F = KC*BANK; // Bet This Much (Adjusted)
    console.log("KC = " + KC);
    console.log("F = " + F);

    // Output Calculated Values to Form
    form.KC.value = decimalFP(KC, 4); 
    form.F.value = decimalFP(F, 2); 
    
} // End kellyBet function.
    
function decimalFP(fpNum,d) {
    // This function will format a floating point number to show the desired number of decimal places.

    fpNum = Math.round(fpNum*Math.pow(10,d))/Math.pow(10,d);
    str = fpNum.toString();
    i = str.indexOf(".");
    if (i>-1) {
        dif = str.length - i;
        while (dif<(d+1)) {
        str += "0";
        dif = str.length - i;
        }
    } else {
        str += ".";
        for (k=0;k<d;k++) {
            str += "0";
        }
    }
    return str;
} // End decimalFP function.
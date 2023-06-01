 

var Cost = function(showPrice){
    console.log("In price function"+showPrice);
    var numSeats = $('#seats option:selected').val();
    if (numSeats === undefined)
        numSeats = 1;
    var price = showPrice;
    var totalPrice = price * numSeats;
    $("#price").empty();
    $('#price').val(totalPrice); 
}
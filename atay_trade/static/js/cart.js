$(document).ready(function(){
    $.ajax({
        type: "GET",
        url: "http://localhost:8000/cart/",
        dataType: "application/json",
        success: function(data) {
            console.log(data);
        },
        error: function(data) {
            console.log("ERR: ", data);
        }
    });
});
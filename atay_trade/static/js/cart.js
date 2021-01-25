$(document).ready(function(){
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue =   decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // add to the cart
    let addButtons = document.getElementsByClassName('add-cart');
    for (let i = 0; i < addButtons.length; i++) {
        addButtons[i].addEventListener('click', function(e) {
            e.preventDefault();
            let productID = this.dataset.product;
            let action = this.dataset.action;
            console.log("productID: ", productID, "Action: ", action);

            console.log("user:", user);
            if (user == "AnonymousUser") {
                console.log("user is not authenticated");
            } else {
                $.ajax({
                    type: "POST",
                    url: "http://localhost:8000/cart/add/",
                    data: JSON.stringify({"productID": productID}),
                    contentType: "application/json",
                    success: function(data) {
                        console.log(data);
                    },
                    error: function(data, err) {
                        console.log("ERR: ", err);
                        console.log(data)
                    }
                });
            }
        });
    }

    //remove from the cart
    let removeButtons = document.getElementsByClassName('remove-cart');
    for (let i = 0; i < removeButtons.length; i++) {
        removeButtons[i].addEventListener('click', function(e) {
            e.preventDefault();
            let productID = this.dataset.product;
            let action = this.dataset.action;
            console.log("productID: ", productID, "Action: ", action);

            console.log("user:", user);
            if (user == "AnonymousUser") {
                console.log("user is not authenticated");
            } else {
                $.ajax({
                    type: "DELETE",
                    url: "http://localhost:8000/cart/remove/",
                    data: JSON.stringify({"productID": productID}),
                    contentType: "application/json",
                    success: function(data) {
                        console.log(data);
                    },
                    error: function(data, err) {
                        console.log("ERR: ", err);
                        console.log(data)
                    }
                });
            }
        });
    }

    //populate the cart
    $.ajax({
        type: "GET",
        url: "http://localhost:8000/cart/",
        contentType: "application/json",
        success: function(data) {
            console.log(data);
        },
        error: function(data, err) {
            console.log("ERR: ", err);
            console.log(data);
        }
    });
});
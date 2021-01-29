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

    // get for the cart
    document.getElementsByClassName('get-cart')[0].addEventListener('click', function(e) {
        e.preventDefault();
        //populate the cart
        $.ajax({
            type: "GET",
            url: "http://localhost:8000/cart/",
            contentType: "application/json",
            success: function(data) {
                $(".single-cart-item").remove();

                let total = data["total_price"];
                $('.summary-total').text("£" + total);

                let productsCount = data["order_items"].length;
                for(let i = 0; i < productsCount; i++) {
                    $(".cart-list").append(
                    `<div class="single-cart-item">
                        <a href="#" class="product-image">
                            <img src=${'static/img/product-img/product-2.jpg'} class="cart-thumb" alt="product cart image">
                        
                            <div class="cart-item-desc">
                            <button data-product="${data["order_items"][i]["product"]["id"]}" data-action="remove" class="product-remove remove-cart" style="background-color: transparent;border: none;"><i class="fa fa-close" aria-hidden="true"></i></button>
                                <span class="badge product-quantity">${data["order_items"][i]["quantity"]}X</span>
                                <h6>${data["order_items"][i]["product"]["name"]}</h6>
                                <!--<p class="size">Size: S</p>-->
                                <!--<p class="color">Color: Red</p>-->
                                <p class="price">£${data["order_items"][i]["product"]["price"].toFixed(2)}</p>
                            </div>
                        </a>
                    </div>`);
                }

                console.log(data);
                let image = data["order_items"][0]["product"]["images"][0]["image"];
            },
            error: function(data, err) {
                console.log("ERR: ", err);
                console.log(data);
            }
        });
    })

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
                        $( ".cart-list" ).append( "<p>Test</p>" );
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
                /*$.ajax({
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
                });*/
            }
        });
    }
});
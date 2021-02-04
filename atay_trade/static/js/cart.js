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

    function tidyCheckoutArea(data) {
        $(".order-details-form").empty();
        $(".order-details-form").append(
            `<li><span>Product</span> <span>Total</span></li>`
        );
        let total = data["total_price"];
        let productsCount = data["order_items"].length;
        for(let i = 0; i < productsCount; i++) {
            let productName = data["order_items"][i]["product"]["name"];
            let productQuantity = data["order_items"][i]["quantity"];
            let productPrice = data["order_items"][i]["product"]["price"].toFixed(2);
            $(".order-details-form").append(`<li><span>${productName} X ${productQuantity}</span> <span>£${productPrice}</span></li>`);
        }
        $(".order-details-form").append(
            `<li><span>Subtotal</span> <span>£${total}</span></li>
            <li><span>Shipping</span> <span>Free</span></li>
            <li><span>Total</span> <span>£${total}</span></li>`
        );
    }

    function populateTheCart() {
        $.ajax({
            type: "GET",
            url: "http://localhost:8000/cart/",
            contentType: "application/json",
            success: function(data) {
                $(".single-cart-item").remove();

                let total = data["total_price"];
                $('.summary-total').text("£" + total);
                $('.count-cart').text(data["items_count"]);

                let image = data["order_items"][0]["product"];
                console.log(image);

                let productsCount = data["order_items"].length;
                for(let i = 0; i < productsCount; i++) {
                    $(".cart-list").append(
                    `<div class="single-cart-item">
                        <a href="/products/${data["order_items"][i]["product"]["id"]}" class="product-image">
                            <img src=${data["order_items"][i]["product"]["images"][0]["image"]} class="cart-thumb" alt="product cart image">
                        
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


                //remove buttons
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
                            console.log("deleting...");
                            $.ajax({
                                type: "DELETE",
                                url: "http://localhost:8000/cart/remove/",
                                data: JSON.stringify({"productID": productID}),
                                contentType: "application/json",
                                success: function(data) {
                                    console.log(data);
                                    populateTheCart();
                                    tidyCheckoutArea(data);
                                },
                                error: function(data, err) {
                                    console.log("ERR: ", err);
                                    console.log(data)
                                }
                            });
                        }
                    }, {once: true});
                }
            },
            error: function(data, err) {
                console.log("ERR: ", err);
                console.log(data);
            }
        });
    }

    populateTheCart();

    // get for the cart
    document.getElementsByClassName('get-cart')[0].addEventListener('click', function(e) {
        e.preventDefault();
        populateTheCart();
    });

    // add buttons
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
                        populateTheCart();
                    },
                    error: function(data, err) {
                        console.log("ERR: ", err);
                        console.log(data)
                    }
                });
            }
        });
    }

});
var csrftoken = getCookie('csrftoken'); //global csrfToken
var guestCart = JSON.parse(getCookie('cart')); //global cart cookie for guests
const DOMAIN_URL = "https://www.ataytrade.co.uk"; //domain URL, http://localhost:8000

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue =   decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

if (guestCart == undefined) {
    guestCart = {};
    document.cookie = "cart=" + JSON.stringify(guestCart) + ";domain=;path=/;samesite=lax;secure";
} 
console.log("GUEST CART:", guestCart);

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
    let orderDetailsForm = $(".order-details-form");
    orderDetailsForm.empty();
    orderDetailsForm.append(
        `<li><span>Product</span> <span>Total</span></li>`
    );

    let subtotal = data["subtotal"];
    if (subtotal != undefined) {
        subtotal = subtotal.toFixed(2);
    }
    let deliveryPrice = data["delivery_price"];
    if (deliveryPrice == 0) { 
        deliveryPrice = "Free"; 
    } else {
        deliveryPrice = "£" + deliveryPrice;
    }
    let total = data["total_price"].toFixed(2);
    let productsCount = data["order_items"].length;
    for(let i = 0; i < productsCount; i++) {
        let productName = data["order_items"][i]["product"]["name"];
        let productQuantity = data["order_items"][i]["quantity"];
        let productPrice = data["order_items"][i]["product"]["price"].toFixed(2);
        let productDiscountedPrice = data["order_items"][i]["product"]["discounted_price"];
        if (productDiscountedPrice != undefined) {
            productDiscountedPrice = productDiscountedPrice.toFixed(2);
            orderDetailsForm.append(`<li><span>${productName} X ${productQuantity}</span> <span>£${productDiscountedPrice}</span></li>`);
        } else {
            orderDetailsForm.append(`<li><span>${productName} X ${productQuantity}</span> <span>£${productPrice}</span></li>`);
        }
        
    }
    orderDetailsForm.append(
        `<li><span>Subtotal</span> <span class="subtotal">£${subtotal}</span></li>
        <li><span>Shipping</span> <span>${deliveryPrice}</span></li>
        <li><span>Total</span> <span class="checkout-total">£${total}</span></li>`
    );
}

function onClickAddButton(e) {
    e.preventDefault();
    let productID = this.dataset.product;

    console.log("user:", user);
    if (user == "AnonymousUser") {
        if (guestCart[productID] == undefined) {
            guestCart[productID] = {'quantity': 1};
        } else {
            guestCart[productID]['quantity'] += 1;
        }
        console.log("GUEST CART", guestCart);
        document.cookie = "cart=" + JSON.stringify(guestCart) + ";domain=;path=/;samesite=lax;secure";
        populateTheCart();
    } else {
        $.ajax({
            type: "POST",
            url: `${DOMAIN_URL}/cart/add/`,
            data: JSON.stringify({"productID": productID}),
            contentType: "application/json",
            success: function(data) {
                console.log(data);
                populateTheCart();
            },
            error: function(data, err) {
                console.log("ERR: ", err);
            }
        });
    }
}

function onClickRemoveButton(e) {
    e.preventDefault();
    let productID = this.dataset.product;

    console.log("user:", user);
    if (user == "AnonymousUser") {
        if (guestCart[productID] != undefined) {
            delete guestCart[productID];
            document.cookie = "cart=" + JSON.stringify(guestCart) + ";domain=;path=/;samesite=lax;secure";
            populateTheCart();
        }
    } else {
        $.ajax({
            type: "DELETE",
            url: `${DOMAIN_URL}/cart/remove/`,
            data: JSON.stringify({"productID": productID}),
            contentType: "application/json",
            success: function(data) {
                console.log(data);
                populateTheCart();
            },
            error: function(data, err) {
                console.log("ERR: ", err);
            }
        });
    }
}

function populateTheCart() {
    $.ajax({
        type: "GET",
        url: `${DOMAIN_URL}/cart/`,
        contentType: "application/json",
        success: function(data) {
            tidyCheckoutArea(data);

            $(".single-cart-item").remove();
            if (data["subtotal"] !== undefined) {
                $('.subtotal').text("£" + data["subtotal"].toFixed(2));
            }
            $('.count-cart').text(data["items_count"]);
            
            if (data["total_price"] !== undefined) {
                $('.summary-total').text("£" + data["total_price"].toFixed(2));
            }
            if (data["delivery_price"] != 0) {
                $('.delivery').text("£" + data["delivery_price"].toFixed(2));   
            } else {
                $('.delivery').text("FREE"); 
            }

            let productsCount;
            if (data["order_items"] === undefined) {
                productsCount = 0 
            } else {
                productsCount = data["order_items"].length;
            }

            for(let i = 0; i < productsCount; i++) {
                let price = data["order_items"][i]["product"]["price"].toFixed(2);
                if (data["order_items"][i]["product"]["discounted_price"] != null) {
                    price = data["order_items"][i]["product"]["discounted_price"].toFixed(2)
                }
                $(".cart-list").append(
                `<div class="single-cart-item">
                    <a href="/products/${data["order_items"][i]["product"]["id"]}" class="product-image">
                        <img src=${data["order_items"][i]["product"]["images"][0]["image"]} class="cart-thumb" alt="product cart image">
                    
                        <div class="cart-item-desc">
                        <button data-product="${data["order_items"][i]["product"]["id"]}" class="product-remove remove-cart" style="background-color: transparent;border: none;"><i class="fa fa-close" aria-hidden="true"></i></button>
                            <span class="badge product-quantity">${data["order_items"][i]["quantity"]}X</span>
                            <h6>${data["order_items"][i]["product"]["name"]}</h6>
                            <!--<p class="size">Size: S</p>-->
                            <!--<p class="color">Color: Red</p>-->
                            <p class="price">£${price}</p>
                        </div>
                    </a>
                </div>`);
            }


            // setup remove buttons handlers
            let removeButtons = document.getElementsByClassName('remove-cart');
            for (let i = 0; i < removeButtons.length; i++) {
                removeButtons[i].addEventListener('click', onClickRemoveButton, {once: true});
            }
        },
        error: function(data, err) {
            console.log("ERR: ", err);
        }
    });
}

$(document).ready(function(){

    populateTheCart();

    // setup cart button handler
    let cardButton = document.getElementsByClassName('get-cart')[0];
    if (cardButton != undefined) {
        cardButton.addEventListener("click", function(e) {
            e.preventDefault();
            populateTheCart();
        });
    }

    // setup add button handlers
    let addButtons = document.getElementsByClassName('add-cart');
    for (let i = 0; i < addButtons.length; i++) {
        addButtons[i].addEventListener('click', onClickAddButton);
    }

    function addToWishlist(productID, heartIndex = undefined, toggleClassListForButtons = false) {
        $.ajax({
            type: "POST",
            url: `${DOMAIN_URL}/wishlist/add/`,
            data: JSON.stringify({"productID": productID}),
            contentType: "application/json",
            success: function() {
                if(heartIndex !== undefined && toggleClassListForButtons) {
                    wishlistHeartIcons[heartIndex].classList.remove('far');
                    wishlistHeartIcons[heartIndex].classList.add('fas');
                    wishlistHeartButtonStates[heartIndex] = 1;
                } else if (heartIndex !== undefined && !toggleClassListForButtons) {
                    heartFavButtonStates[heartIndex] = 1;
                }
            },
            error: function(data, err) {
                console.log("ERR: ", err);
            }
        });
    }
    
    function removeFromWishlist(productID, heartIndex, toggleClassListForButtons = false) {
        $.ajax({
            type: "DELETE",
            url: `${DOMAIN_URL}/wishlist/remove/`,
            data: JSON.stringify({"productID": productID}),
            contentType: "application/json",
            success: function() {
                if(heartIndex !== undefined && toggleClassListForButtons) {
                    wishlistHeartIcons[heartIndex].classList.remove('fas');
                    wishlistHeartIcons[heartIndex].classList.add('far');
                    wishlistHeartButtonStates[heartIndex] = 0;
                } else if (heartIndex !== undefined && !toggleClassListForButtons) {
                    heartFavButtonStates[heartIndex] = 1;
                }
            },
            error: function(data, err) {
                console.log("ERR: ", err);
            }
        });
    }

    // These heart buttons are only inside the wishlist page
    let wishlistHeartButtons = document.getElementsByClassName('btn-primary-like');
    let wishlistHeartButtonStates = [];
    let wishlistHeartIcons = document.getElementsByClassName("wishlist-heart");
    for(let i = 0; i < wishlistHeartButtons.length; i++) {
        wishlistHeartButtonStates.push(1);
        wishlistHeartButtons[i].addEventListener('click', function(e) {
            e.preventDefault();
            let productID = this.dataset.product;

            if(wishlistHeartButtonStates[i] == 1) {
                removeFromWishlist(productID, i, true);
            } else if (wishlistHeartButtonStates[i] == 0) {
                addToWishlist(productID, i, true);
            }
        });
    }

    // These heart buttons are everywhere outside of wishlist page
    let heartFavButtons = document.getElementsByClassName('favme');
    let heartFavButtonStates = [];
    for(let i = 0; i < heartFavButtons.length; i++) {
        if(heartFavButtons[i].className == "favme fa fa-heart") {
            heartFavButtonStates.push(0);
        } else if (heartFavButtons[i].className == "favme fa fa-heart active") {
            heartFavButtonStates.push(1);
        }

        heartFavButtons[i].addEventListener('click', function(e) {
            e.preventDefault();
            let productID = this.dataset.product;

            if(heartFavButtonStates[i] == 1) {
                removeFromWishlist(productID, i);
            } else if (heartFavButtonStates[i] == 0) {
                addToWishlist(productID, i);
            } 
        })
    }

    // setup catalog price filterer handler
    let priceFiltererForm = document.getElementsByClassName("price-filterer-form")[0];
    if (priceFiltererForm != undefined) {
        priceFiltererForm.addEventListener('submit', function(e) {
            let rangePriceText =  document.getElementsByClassName('range-price')[0].textContent;
            rangePriceText = rangePriceText.slice(7).split("-");
            rangePriceText[0] = rangePriceText[0].trim().slice(1);
            rangePriceText[1] = rangePriceText[1].trim().slice(1);
            rangePriceText = rangePriceText.join("-");
            $(".priceRange").val(rangePriceText);
        });
    }
});
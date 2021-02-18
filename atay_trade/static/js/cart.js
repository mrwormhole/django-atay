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
    var guestCart = JSON.parse(getCookie('cart'));
    if (guestCart == undefined) {
        guestCart = {};
        document.cookie = "cart=" + JSON.stringify(guestCart) + ";domain=;path=/";
    } 
    console.log("GUEST CART:", guestCart)

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
            $(".order-details-form").append(`<li><span>${productName} X ${productQuantity}</span> <span>£${productPrice}</span></li>`);
        }
        $(".order-details-form").append(
            `<li><span>Subtotal</span> <span>£${subtotal}</span></li>
            <li><span>Shipping</span> <span>${deliveryPrice}</span></li>
            <li><span>Total</span> <span class="checkout-total">£${total}</span></li>`
        );
    }

    function populateTheCart() {
        $.ajax({
            type: "GET",
            url: "http://localhost:8000/cart/",
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


                //remove buttons
                let removeButtons = document.getElementsByClassName('remove-cart');
                for (let i = 0; i < removeButtons.length; i++) {
                    removeButtons[i].addEventListener('click', function(e) {
                        e.preventDefault();
                        let productID = this.dataset.product;
                        console.log("productID: ", productID);

                        console.log("user:", user);
                        if (user == "AnonymousUser") {
                            console.log("user is not authenticated");
                            if (guestCart[productID] != undefined) {
                                delete guestCart[productID];
                                document.cookie = "cart=" + JSON.stringify(guestCart) + ";domain=;path=/";
                                populateTheCart()
                            }
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
            console.log("productID: ", productID);

            console.log("user:", user);
            if (user == "AnonymousUser") {
                console.log("user is not authenticated");
                if (guestCart[productID] == undefined) {
                    guestCart[productID] = {'quantity': 1};
                } else {
                    guestCart[productID]['quantity'] += 1;
                }
                console.log("GUEST CART", guestCart);
                document.cookie = "cart=" + JSON.stringify(guestCart) + ";domain=;path=/";
                populateTheCart();
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
                        console.log(data);
                    }
                });
            }
        });
    }

    function addToWishlist(productID, heartIndex = undefined, toggleClassListForButtons = false) {
        $.ajax({
            type: "POST",
            url: "http://localhost:8000/wishlist/add/",
            data: JSON.stringify({"productID": productID}),
            contentType: "application/json",
            success: function(data) {
                console.log(data);
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
                console.log(data);
            }
        });
    }

    function removeFromWishlist(productID, heartIndex, toggleClassListForButtons = false) {
        $.ajax({
            type: "DELETE",
            url: "http://localhost:8000/wishlist/remove/",
            data: JSON.stringify({"productID": productID}),
            contentType: "application/json",
            success: function(data) {
                console.log(data);
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
                console.log(data);
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

    //catalog page
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

    function isBillingFormEmpty(data) {
        if (data.firstName.trim() == "" ||  data.lastName.trim() == "" ||
            data.emailAddress.trim() == "" || data.country.trim() == "" ||
            data.streetAddress.trim() == "" || data.postcode.trim() == "" ||
            data.city.trim() == "" || data.phoneNumber.trim() == "") {
                return true;
        }
        return false;    
    }

    var paymentFormData = {
        firstName: "",
        lastName: "",
        emailAddress: "",
        country: "",
        streetAddress: "",
        postcode: "",
        city: "",
        phoneNumber: ""
    }
    //checkout page
    let checkoutBillingForm = document.getElementsByClassName("checkout-billing-form")[0];
    if (checkoutBillingForm != undefined) {
        checkoutBillingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            let firstNameInput = e.target.elements.first_name;
            let lastNameInput = e.target.elements.last_name;
            let emailAddressInput = e.target.elements.email_address;
            let countryInput = e.target.elements.country;
            let streetAddressInput = e.target.elements.country;
            let postcodeInput = e.target.elements.postcode;
            let cityInput = e.target.elements.city;
            let phoneNumberInput = e.target.elements.phone_number;
            
            const billingFormData = {
                firstName: firstNameInput.value,
                lastName: lastNameInput.value,
                emailAddress: emailAddressInput.value,
                country: countryInput.value,
                streetAddress: streetAddressInput.value,
                postcode: postcodeInput.value,
                city: cityInput.value,
                phoneNumber: phoneNumberInput.value
            };
            let notValidForm = isBillingFormEmpty(billingFormData);
            if (notValidForm) {
                $("#notification-danger").text("Your order is not being confirmed! Please make sure that you fill all the fields.")
                $("#notification-danger").attr("class", "alert alert-danger");
                return
            } else {
                $("#notification-danger").attr("class", "alert alert-danger d-none");
            }

            let summaryTotal = document.getElementsByClassName("checkout-total")[0].textContent;
            $("input[name='total_price']").val(summaryTotal.slice(1));
            if($("input[name='total_price']").val() == 0) {
                $("#notification-danger").text("Your cart is currently being empty! Please consider adding something :)")
                $("#notification-danger").attr("class", "alert alert-warning");
                return
            } else {
                $("#notification-danger").attr("class", "alert alert-danger d-none");
            }

            $("#payment-accordion-options").attr("class", "collapse show");
            let confirmationButton = document.getElementById("billing-confirmation-button");
            if (confirmationButton != undefined) {
                confirmationButton.className = "d-none";
                firstNameInput.readOnly = true;
                lastNameInput.readOnly = true;
                emailAddressInput = true;
                countryInput = true;
                streetAddressInput = true;
                postcodeInput = true;
                cityInput = true;
                phoneNumberInput = true;
            }
            
            paymentFormData.firstName = billingFormData.lastName;
            paymentFormData.lastName = billingFormData.lastName;
            paymentFormData.emailAddress = billingFormData.emailAddress;
            paymentFormData.country = billingFormData.country;
            paymentFormData.streetAddress = billingFormData.streetAddress;
            paymentFormData.postcode = billingFormData.postcode;
            paymentFormData.city = billingFormData.city;
            paymentFormData.phoneNumber = billingFormData.phoneNumber;
        });
    }

    function initPayPalButton() {
        paypal.Buttons({
          style: {
            shape: 'pill',
            color: 'blue',
            layout: 'vertical',
            label: 'paypal',
            
          },
    
          createOrder: function(data, actions) {
            let summaryTotal = document.getElementsByClassName("checkout-total")[0].textContent;
            let value = '' + parseFloat(summaryTotal.slice(1)).toFixed(2);
    
            return actions.order.create({
              purchase_units: [{"amount":{"currency_code":"GBP","value":value}}]
            });
          },
    
          onApprove: function(data, actions) {
            return actions.order.capture().then(function(details) {
              alert('Transaction completed by ' + details.payer.name.given_name + '!');
              //POST to the endpoint
            });
          },
    
          onError: function(err) {
            console.log(err);
          }
        }).render('#paypal-button-container');
      }
      initPayPalButton();
    

});
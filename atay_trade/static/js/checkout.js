$(document).ready(function() {
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

    function getStockStatus(data) {
        return $.ajax({
            type: "POST",
            url: "http://localhost:8000/stocks/check/",
            data: JSON.stringify(data),
            contentType: "application/json",
            success: function(data) {
                console.log(data);
            },
            error: function(data, err) {
                console.log("ERR: ", err);
                console.log(data);
            }
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
        phoneNumber: "",
        totalPrice: ""
    }

    let checkoutBillingForm = document.getElementsByClassName("checkout-billing-form")[0];
    if (checkoutBillingForm != undefined) {
        checkoutBillingForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            let firstNameInput = e.target.elements.first_name;
            let lastNameInput = e.target.elements.last_name;
            let emailAddressInput = e.target.elements.email_address;
            let countryInput = e.target.elements.country;
            let streetAddressInput = e.target.elements.street_address;
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
            } 

            try {
                let stockStatus = await getStockStatus(billingFormData);
                console.log("STOCK STATUS", stockStatus);
                if (stockStatus["error"] != undefined) {
                    $("#notification-danger").text(`Error occured: ${stockStatus["error"]}`);
                    $("#notification-danger").attr("class", "alert alert-danger");
                    return
                } else if (stockStatus["message"] != undefined) {
                    $("#notification-danger").text(stockStatus["message"]);
                    $("#notification-danger").attr("class", "alert alert-warning");
                    return
                } else if (stockStatus["success"] != undefined) {
                    $("#notification-danger").attr("class", "alert alert-danger d-none");
                }
            } catch {
                console.log("AWAIT EXCEPTION OCCURED");
                return
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
            
            paymentFormData.firstName = billingFormData.firstName;
            paymentFormData.lastName = billingFormData.lastName;
            paymentFormData.emailAddress = billingFormData.emailAddress;
            paymentFormData.country = billingFormData.country;
            paymentFormData.streetAddress = billingFormData.streetAddress;
            paymentFormData.postcode = billingFormData.postcode;
            paymentFormData.city = billingFormData.city;
            paymentFormData.phoneNumber = billingFormData.phoneNumber;
            paymentFormData.totalPrice = $("input[name='total_price']").val();
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
                $.ajax({
                    type: "POST",
                    url: "http://localhost:8000/checkout/",
                    data: JSON.stringify(paymentFormData),
                    contentType: "application/json",
                    success: function(data) {
                        console.log(data);
                        $.ajax({
                            type: "POST",
                            url: "http://localhost:8000/orders/process/",
                            data: JSON.stringify(paymentFormData),
                            contentType: "application/json",
                            success: function(orderStatus) {
                                if (orderStatus["error"] != undefined) {
                                    $("#notification-danger").text(`Error occured: ${orderStatus["error"]}`);
                                    $("#notification-danger").attr("class", "alert alert-danger");
                                } else if (orderStatus["message"] != undefined) {
                                    $("#notification-danger").text(orderStatus["message"]);
                                    $("#notification-danger").attr("class", "alert alert-warning");
                                    return
                                } else if (orderStatus["success"] != undefined) {
                                    $('#notification-success').text(orderStatus["success"]);
                                    $('#notification-success').attr("class", "alert alert-success");
                                    $("#notification-danger").attr("class", "alert alert-danger d-none");
                                    document.cookie = "cart=" + ";domain=;path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT";
                                }
                            },
                            error: function(data, err) {
                                console.log("ERR: ", err);
                                console.log(data);
                            }
                        });
                    },
                    error: function(data, err) {
                        console.log("ERR: ", err);
                        console.log(data);
                        //show error for the dom
                    }
                });
                //alert('Transaction completed by ' + details.payer.name.given_name + '!');
            });
        },

        onError: function(err) {
            console.log(err);
        }
        }).render('#paypal-button-container');
    }

    initPayPalButton();
});
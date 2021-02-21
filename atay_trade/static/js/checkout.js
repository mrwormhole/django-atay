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
};

function getStockStatus(data) {
    return $.ajax({
        type: "POST",
        url: `${DOMAIN_URL}/stocks/check/`,
        data: JSON.stringify(data),
        contentType: "application/json"
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

function clearBillingForm() {
    let formInputs = document.querySelectorAll(".checkout-billing-form input");
    //first one is csrf token in the inputs
    for(let i = 1; i < formInputs.length; i++) {
        formInputs[i].value = "";
        formInputs[i].readOnly = false;
    }
    let confirmationButton = document.getElementById("billing-confirmation-button");
    if (confirmationButton != undefined) {
        confirmationButton.className = "btn essence-btn";
    }
    $("#payment-accordion-options").attr("class", "collapse");
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
                    url: `${DOMAIN_URL}/checkout/`,
                    data: JSON.stringify(paymentFormData),
                    contentType: "application/json",
                    success: function() {
                        $.ajax({
                            type: "POST",
                            url: `${DOMAIN_URL}/orders/process/`,
                            data: JSON.stringify(paymentFormData),
                            contentType: "application/json",
                            success: function(orderStatus) {
                                let notificationDanger = $("#notification-danger");
                                let notificationSuccess =  $('#notification-success');
                                if (orderStatus["error"] != undefined) {
                                    notificationDanger.text(`Error occured: ${orderStatus["error"]}`);
                                    notificationDanger.attr("class", "alert alert-danger");
                                } else if (orderStatus["message"] != undefined) {
                                    notificationDanger.text(orderStatus["message"]);
                                    notificationDanger.attr("class", "alert alert-warning");
                                    return
                                } else if (orderStatus["success"] != undefined) {
                                    notificationSuccess.text(orderStatus["success"]);
                                    notificationSuccess.attr("class", "alert alert-success");
                                    notificationDanger.attr("class", "alert alert-danger d-none");
                                    document.cookie = "cart=" + ";domain=;path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT";
                                }
                                clearBillingForm();
                                populateTheCart();
                            },
                            error: function(data, err) {
                                console.log("ERR: ", err);
                            }
                        });
                    },
                    error: function(data, err) {
                        console.log("ERR: ", err);
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

$(document).ready(function() {

    //setup checkout billing form handler
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
            
            let notificationDanger = $("#notification-danger");
            let notValidForm = isBillingFormEmpty(billingFormData);
            if (notValidForm) {
                notificationDanger.text("Your order is not being confirmed! Please make sure that you fill all the fields.")
                notificationDanger.attr("class", "alert alert-danger");
                return
            }
            
            let summaryTotal = document.getElementsByClassName("checkout-total")[0].textContent;
            let totalPriceInput = $("input[name='total_price']");
            totalPriceInput.val(summaryTotal.slice(1));
            if(totalPriceInput.val() == 0) {
                notificationDanger.text("Your cart is currently being empty! Please consider adding something :)")
                notificationDanger.attr("class", "alert alert-warning");
                return
            } else {
                notificationDanger.attr("class", "alert alert-danger d-none");
            }

            try {
                let stockStatus = await getStockStatus(billingFormData);
                console.log("STOCK STATUS", stockStatus);
                if (stockStatus["error"] != undefined) {
                    notificationDanger.text(`Error occured: ${stockStatus["error"]}`);
                    notificationDanger.attr("class", "alert alert-danger");
                    return
                } else if (stockStatus["message"] != undefined) {
                    notificationDanger.text(stockStatus["message"]);
                    notificationDanger.attr("class", "alert alert-warning");
                    return
                } else if (stockStatus["success"] != undefined) {
                   notificationDanger.attr("class", "alert alert-danger d-none");
                }
            } catch {
                console.log("AWAIT EXCEPTION OCCURED");
                return
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
            paymentFormData.totalPrice = totalPriceInput.val();
        });
    }

    initPayPalButton();
});
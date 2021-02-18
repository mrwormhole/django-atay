$(document).ready(function() {
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
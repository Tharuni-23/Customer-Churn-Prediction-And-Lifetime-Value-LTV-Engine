// ============================================================
// TELCOCONNECT - REGISTER JAVASCRIPT
// ============================================================


document.addEventListener(
    "DOMContentLoaded",
    function () {

        // --------------------------------------------------------
        // GET FORM ELEMENTS
        // --------------------------------------------------------

        const registerForm =
            document.getElementById(
                "registerForm"
            );

        const nameInput =
            document.getElementById(
                "name"
            );

        const emailInput =
            document.getElementById(
                "email"
            );

        const passwordInput =
            document.getElementById(
                "password"
            );

        const confirmInput =
            document.getElementById(
                "confirm"
            );

        const message =
            document.getElementById(
                "msg"
            );


        // --------------------------------------------------------
        // SAFETY CHECK
        // --------------------------------------------------------

        if (!registerForm) {
            return;
        }


        // --------------------------------------------------------
        // FORM SUBMISSION
        // --------------------------------------------------------

        registerForm.addEventListener(
            "submit",
            function (event) {

                event.preventDefault();


                // ------------------------------------------------
                // GET VALUES
                // ------------------------------------------------

                const name =
                    nameInput.value.trim();

                const email =
                    emailInput.value.trim();

                const password =
                    passwordInput.value;

                const confirmPassword =
                    confirmInput.value;


                // Clear previous message

                message.textContent = "";


                // ------------------------------------------------
                // REQUIRED FIELD CHECK
                // ------------------------------------------------

                if (
                    !name ||
                    !email ||
                    !password ||
                    !confirmPassword
                ) {

                    message.textContent =
                        "Please fill in all fields.";

                    message.style.color =
                        "#d32f2f";

                    return;
                }


                // ------------------------------------------------
                // EMAIL CHECK
                // ------------------------------------------------

                const emailPattern =
                    /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


                if (
                    !emailPattern.test(email)
                ) {

                    message.textContent =
                        "Please enter a valid email address.";

                    message.style.color =
                        "#d32f2f";

                    return;
                }


                // ------------------------------------------------
                // PASSWORD LENGTH
                // ------------------------------------------------

                if (
                    password.length < 6
                ) {

                    message.textContent =
                        "Password must contain at least 6 characters.";

                    message.style.color =
                        "#d32f2f";

                    return;
                }


                // ------------------------------------------------
                // PASSWORD MATCH
                // ------------------------------------------------

                if (
                    password !==
                    confirmPassword
                ) {

                    message.textContent =
                        "Passwords do not match.";

                    message.style.color =
                        "#d32f2f";

                    return;
                }


                // ------------------------------------------------
                // TEMPORARY FRONTEND REGISTRATION
                //
                // FastAPI + PostgreSQL will be added later.
                // ------------------------------------------------

                console.log(
                    "Registration submitted"
                );

                console.log(
                    "Name:",
                    name
                );

                console.log(
                    "Email:",
                    email
                );


                // ------------------------------------------------
                // TEMPORARY SESSION DATA
                // ------------------------------------------------

                sessionStorage.setItem(
                    "customerName",
                    name
                );

                sessionStorage.setItem(
                    "customerEmail",
                    email
                );


                // Temporary customer ID
                sessionStorage.setItem(
                    "customerID",
                    "CUST-XXXXX"
                );


                // ------------------------------------------------
                // SUCCESS MESSAGE
                // ------------------------------------------------

                message.textContent =
                    "Account created successfully!";

                message.style.color =
                    "#388e3c";


                // ------------------------------------------------
                // DISABLE BUTTON
                // ------------------------------------------------

                const submitButton =
                    registerForm.querySelector(
                        "button[type='submit']"
                    );


                if (submitButton) {

                    submitButton.disabled =
                        true;

                    submitButton.textContent =
                        "Account Created";

                }


                // ------------------------------------------------
                // RETURN TO LOGIN
                // ------------------------------------------------

                setTimeout(
                    function () {

                        window.location.href =
                            "index.html";

                    },
                    1000
                );

            }
        );

    }
);
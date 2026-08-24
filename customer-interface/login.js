// ============================================================
// TELCOCONNECT - LOGIN JAVASCRIPT
// ============================================================


document.addEventListener(
    "DOMContentLoaded",
    function () {

        // --------------------------------------------------------
        // GET ELEMENTS
        // --------------------------------------------------------

        const loginForm =
            document.getElementById(
                "loginForm"
            );

        const emailInput =
            document.getElementById(
                "email"
            );

        const passwordInput =
            document.getElementById(
                "password"
            );

        const rememberMe =
            document.getElementById(
                "rememberMe"
            );

        const loginMessage =
            document.getElementById(
                "loginMessage"
            );

        const forgotPassword =
            document.getElementById(
                "forgotPassword"
            );


        // --------------------------------------------------------
        // SAFETY CHECK
        // --------------------------------------------------------

        if (!loginForm) {
            return;
        }


        // --------------------------------------------------------
        // LOGIN
        // --------------------------------------------------------

        loginForm.addEventListener(
            "submit",
            function (event) {

                event.preventDefault();


                const email =
                    emailInput.value.trim();

                const password =
                    passwordInput.value;


                // ------------------------------------------------
                // VALIDATION
                // ------------------------------------------------

                if (!email || !password) {

                    loginMessage.textContent =
                        "Please enter email and password.";

                    loginMessage.style.color =
                        "#d32f2f";

                    return;
                }


                // ------------------------------------------------
                // TEMPORARY FRONTEND LOGIN
                //
                // FastAPI + PostgreSQL will replace this later.
                // ------------------------------------------------

                const customerName =
                    email
                        .split("@")[0];


                sessionStorage.setItem(
                    "customerName",
                    customerName
                );


                sessionStorage.setItem(
                    "customerEmail",
                    email
                );


                sessionStorage.setItem(
                    "customerID",
                    "CUST-XXXXX"
                );


                // ------------------------------------------------
                // REMEMBER ME
                // ------------------------------------------------

                if (
                    rememberMe &&
                    rememberMe.checked
                ) {

                    localStorage.setItem(
                        "rememberEmail",
                        email
                    );

                } else {

                    localStorage.removeItem(
                        "rememberEmail"
                    );

                }


                // ------------------------------------------------
                // SUCCESS
                // ------------------------------------------------

                loginMessage.textContent =
                    "Login successful. Redirecting...";

                loginMessage.style.color =
                    "#388e3c";


                // ------------------------------------------------
                // REDIRECT TO DASHBOARD
                // ------------------------------------------------

                setTimeout(
                    function () {

                        window.location.href =
                            "dashboard.html";

                    },
                    500
                );

            }
        );


        // --------------------------------------------------------
        // FORGOT PASSWORD
        // --------------------------------------------------------

        if (forgotPassword) {

            forgotPassword.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    alert(
                        "Password recovery will be connected later."
                    );

                }
            );

        }


        // --------------------------------------------------------
        // LOAD REMEMBERED EMAIL
        // --------------------------------------------------------

        const rememberedEmail =
            localStorage.getItem(
                "rememberEmail"
            );


        if (
            rememberedEmail &&
            emailInput
        ) {

            emailInput.value =
                rememberedEmail;


            if (rememberMe) {

                rememberMe.checked =
                    true;

            }

        }

    }
);
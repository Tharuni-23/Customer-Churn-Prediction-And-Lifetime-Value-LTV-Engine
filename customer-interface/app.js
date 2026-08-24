/* ============================================================
   TELCOCONNECT - SHARED APPLICATION JAVASCRIPT
   ============================================================ */


/* ============================================================
   THEME
   ============================================================ */

/*
 * Apply the saved theme when the page opens.
 */
function initTheme() {

    const savedTheme =
        localStorage.getItem(
            "customerTheme"
        );


    const darkMode =
        savedTheme === "dark";


    document.body.classList.toggle(
        "dark",
        darkMode
    );


    updateThemeButton();
}



/*
 * Update the moon/sun button.
 */
function updateThemeButton() {

    const themeButton =
        document.getElementById(
            "themeToggle"
        );


    if (!themeButton) {
        return;
    }


    const darkMode =
        document.body.classList.contains(
            "dark"
        );


    if (darkMode) {

        themeButton.textContent =
            "☀️";

        themeButton.setAttribute(
            "aria-label",
            "Switch to light mode"
        );

    } else {

        themeButton.textContent =
            "🌙";

        themeButton.setAttribute(
            "aria-label",
            "Switch to dark mode"
        );

    }

}


/*
 * Toggle light/dark mode.
 */
function toggleTheme() {

    const darkMode =
        !document.body.classList.contains(
            "dark"
        );


    document.body.classList.toggle(
        "dark",
        darkMode
    );


    localStorage.setItem(
        "customerTheme",
        darkMode
            ? "dark"
            : "light"
    );


    updateThemeButton();

}



/* ============================================================
   CUSTOMER INFORMATION
   ============================================================ */


/*
 * Get temporary customer information.
 *
 * Later this information will come from FastAPI.
 */
function getCustomerInformation() {

    return {

        name:
            sessionStorage.getItem(
                "customerName"
            ) || "Customer",

        email:
            sessionStorage.getItem(
                "customerEmail"
            ) || "customer@example.com",

        customerID:
            sessionStorage.getItem(
                "customerID"
            ) || "CUST-XXXXX"

    };

}


/*
 * Display customer information
 * wherever data attributes are used.
 */
function loadCustomerInformation() {

    const customer =
        getCustomerInformation();


    document
        .querySelectorAll(
            "[data-customer-name]"
        )
        .forEach(
            function (element) {

                /*
                 * Avatar gets only the first letter.
                 */
                if (
                    element.classList.contains(
                        "avatar"
                    )
                ) {

                    element.textContent =
                        customer.name
                            .charAt(0)
                            .toUpperCase();

                } else {

                    element.textContent =
                        customer.name;

                }

            }
        );


    document
        .querySelectorAll(
            "[data-customer-email]"
        )
        .forEach(
            function (element) {

                element.textContent =
                    customer.email;

            }
        );


    document
        .querySelectorAll(
            "[data-customer-id]"
        )
        .forEach(
            function (element) {

                element.textContent =
                    customer.customerID;

            }
        );

}



/* ============================================================
   LOGOUT
   ============================================================ */

function setupLogout() {

    const logoutButton =
        document.getElementById(
            "logoutButton"
        );


    if (!logoutButton) {
        return;
    }


    logoutButton.addEventListener(
        "click",
        function () {

            /*
             * Remove temporary session data.
             */
            sessionStorage.removeItem(
                "customerName"
            );

            sessionStorage.removeItem(
                "customerEmail"
            );

            sessionStorage.removeItem(
                "customerID"
            );


            /*
             * Return to login.
             */
            window.location.href =
                "index.html";

        }
    );

}



/* ============================================================
   INITIALIZATION
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initTheme();

        loadCustomerInformation();

        setupLogout();

        const themeButton =
            document.getElementById(
                "themeToggle"
            );


        if (themeButton) {

            themeButton.addEventListener(
                "click",
                toggleTheme
            );

        }

    }
);
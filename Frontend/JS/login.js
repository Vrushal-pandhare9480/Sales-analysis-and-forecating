function showOTPForm(email) {

    const loginBox =
        document.querySelector(".login-box");


    loginBox.innerHTML = `

        <h1>Sales Analysis</h1>

        <h2>Verify Your Email</h2>

        <p>
            Enter the OTP sent to
            <br>
            <strong>${email}</strong>
        </p>

        <form id="otpForm">

            <input
                type="text"
                id="otp"
                placeholder="Enter 6-digit OTP"
                maxlength="6"
                required
            >

            <button type="submit">
                Verify & Login
            </button>

            <p id="otpMessage"></p>

        </form>

    `;


    const otpForm =
        document.getElementById("otpForm");


    otpForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const otp =
                document.getElementById("otp").value.trim();


            const otpMessage =
                document.getElementById("otpMessage");


            otpMessage.innerText =
                "Verifying OTP...";


            try {

                const response = await fetch(
                    "https://sales-analysis-and-forecating.onrender.com/auth/verify-otp",
                    {

                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body: JSON.stringify({

                            email: email,

                            otp: otp

                        })

                    }
                );


                const data =
                    await response.json();


                console.log(
                    "Verify OTP Response:",
                    data
                );


                if (
                    response.ok &&
                    data.success
                ) {

                    otpMessage.innerText =
                        "Email verified successfully!";


                    // Save a simple client-side verified session
                    localStorage.setItem("session_token", "verified");
                    localStorage.setItem("user_email", email);

                    // Dashboard
                    setTimeout(function () {

                        window.location.href =
                            "index.html";

                    }, 700);

                }
                else {

                    otpMessage.innerText =
                        data.detail ||
                        "Invalid OTP.";

                }

            }
            catch (error) {

                console.error(
                    "Verify OTP Error:",
                    error
                );

                otpMessage.innerText =
                    "Unable to connect to server.";

            }

        }
    );

}

const loginForm = document.getElementById("loginForm");

const loginMessage =
    document.getElementById("loginMessage");


loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const email =
        document.getElementById("email").value.trim();




    loginMessage.innerText =
        "Verifying...";


    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/auth/send-otp",
            {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    email: email,

                    // captcha_token: captchaToken

                })

            }
        );


        const data =
            await response.json();


        console.log(
            "Send OTP Response:",
            data
        );


        if (response.ok && data.success) {

            loginMessage.innerText =
                "OTP sent successfully.";

            // Move to OTP screen
            showOTPForm(email);

        }
        else {

            loginMessage.innerText =
                data.detail ||
                "Verification failed.";

        }

    }
    catch (error) {

        console.error(
            "Send OTP Error:",
            error
        );

        loginMessage.innerText =
            "Unable to connect to server.";


    }

});
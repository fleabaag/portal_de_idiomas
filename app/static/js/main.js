document.addEventListener("DOMContentLoaded", function () {

    // Mostrar / ocultar contraseña
    function setupPasswordToggle(
        buttonId,
        inputId,
        iconId
    ) {
        const button = document.getElementById(buttonId);
        const input = document.getElementById(inputId);
        const icon = document.getElementById(iconId);

        if (!button || !input || !icon) return;

        button.addEventListener("click", () => {
            const hidden = input.type === "password";

            input.type = hidden ? "text" : "password";

            icon.src = hidden
                ? "/static/img/cover.png"
                : "/static/img/view.png";
        });
    }

    setupPasswordToggle(
        "togglePassword",
        "password",
        "eyeIcon"
    );

    setupPasswordToggle(
        "toggleConfirmPassword",
        "confirm_password",
        "confirmEyeIcon"
    );


    // Ocultar alertas
    setTimeout(function () {
        const alerts = document.querySelectorAll(".flash-alert");

        alerts.forEach(function (alert) {
            alert.style.transition = "opacity 0.5s ease";
            alert.style.opacity = "0";

            setTimeout(function () {
                alert.remove();
            }, 300);
        });

    }, 3000);

});
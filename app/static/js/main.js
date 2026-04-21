document.addEventListener("DOMContentLoaded", function () {

    // Mostrar / ocultar contraseña
    const toggleBtn = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("password");
    const eyeIcon = document.getElementById("eyeIcon");

    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener("click", function () {
            const isHidden = passwordInput.type === "password";

            passwordInput.type = isHidden ? "text" : "password";
            eyeIcon.src = isHidden
                ? "/static/img/cover.png"
                : "/static/img/view.png";
        });
    }

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
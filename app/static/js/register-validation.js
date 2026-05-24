document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector("form");

    if (!form) return;

    function showFlash(message, type = "validation") {

        document.querySelectorAll(".flash-alert.dynamic")
            .forEach(alert => alert.remove());

        const flash = document.createElement("div");

        flash.className = `flash-alert ${type} dynamic`;
        flash.textContent = message;

        form.prepend(flash);

        setTimeout(() => {
            flash.style.opacity = "0";
            setTimeout(() => flash.remove(), 400);
        }, 5000);
    }

    form.addEventListener("submit", function (e) {

        const password =
            document.querySelector('input[name="password"]').value.trim();

        const confirmPassword =
            document.querySelector('input[name="confirm_password"]').value.trim();

        const email =
            document.querySelector('input[name="email"]').value.trim();

        const passwordRegex =
            /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

        const emailRegex =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            e.preventDefault();
            showFlash("Ingresa un correo electrónico válido");
            return;
        }

        if (!passwordRegex.test(password)) {
            e.preventDefault();
            showFlash(
                "La contraseña debe tener mínimo 8 caracteres, una mayúscula, una minúscula y un número"
            );
            return;
        }

        if (password !== confirmPassword) {
            e.preventDefault();
            showFlash("Las contraseñas no coinciden");
            return;
        }
    });

    const passwordInput =
        document.querySelector('input[name="password"]');

    const confirmInput =
        document.querySelector('input[name="confirm_password"]');

    confirmInput.addEventListener("input", () => {

        if (
            confirmInput.value &&
            passwordInput.value !== confirmInput.value
        ) {
            confirmInput.style.borderColor = "var(--alert-validation)";
        } else {
            confirmInput.style.borderColor = "";
        }
    });

});
document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector("form");

    if (!form) return;

    form.addEventListener("submit", function (e) {

        const password =
            document.querySelector('input[name="password"]').value;

        const confirmPassword =
            document.querySelector('input[name="confirm_password"]').value;

        const regex =
            /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

        // Password segura
        if (!regex.test(password)) {

            e.preventDefault();

            alert(
                "La contraseña debe tener:\n" +
                "- mínimo 8 caracteres\n" +
                "- una mayúscula\n" +
                "- una minúscula\n" +
                "- un número"
            );

            return;
        }

        // Confirmación
        if (password !== confirmPassword) {

            e.preventDefault();

            alert("Las contraseñas no coinciden");
        }

        // Validar email
        const email =
            document.querySelector('input[name="email"]').value;

        const emailRegex =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {

            e.preventDefault();

            alert("Ingresa un correo electrónico válido");

            return;
        }

    });

});
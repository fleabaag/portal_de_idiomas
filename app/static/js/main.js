document.addEventListener("DOMContentLoaded", function () {

    // Mostrar / ocultar contraseña
    function setupPasswordToggle(buttonId, inputId, iconId) {
        const button = document.getElementById(buttonId);
        const input = document.getElementById(inputId);
        const icon = document.getElementById(iconId);

        if (!button || !input || !icon) return;

        button.addEventListener("click", () => {
            const hidden = input.type === "password";
            input.type = hidden ? "text" : "password";
            icon.src = hidden ? "/static/img/cover.png" : "/static/img/view.png";
        });
    }

    setupPasswordToggle("togglePassword", "password", "eyeIcon");
    setupPasswordToggle("toggleConfirmPassword", "confirm_password", "confirmEyeIcon");

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

    // Toggle sidebar
    const toggle = document.getElementById("sidebar-toggle");
    const sidebar = document.getElementById("sidebar");

    if (toggle && sidebar) {
        toggle.addEventListener("click", (e) => {
            e.preventDefault();
            sidebar.classList.toggle("sidebar-collapsed");
            localStorage.setItem("sidebar-collapsed", sidebar.classList.contains("sidebar-collapsed"));
        });

        // Restaurar estado previo de la sidebar
        if (localStorage.getItem("sidebar-collapsed") === "true") {
            sidebar.classList.add("sidebar-collapsed");
        }
    }

    // Modal para crear curso
    const btnAddCourse = document.querySelector(".btn-add-course");
    const modalCurso = document.getElementById("modal-crear-curso");
    const closeBtnModal = document.querySelector(".modal-close");

    if (btnAddCourse && modalCurso) {
        btnAddCourse.addEventListener("click", () => {
            modalCurso.style.display = "flex";
        });
    }

    if (closeBtnModal) {
        closeBtnModal.addEventListener("click", () => {
            modalCurso.style.display = "none";
        });
    }

    if (modalCurso) {
        window.addEventListener("click", (event) => {
            if (event.target === modalCurso) {
                modalCurso.style.display = "none";
            }
        });
    }

    // Confirmar archivación de curso
    const formArchivar = document.querySelectorAll(".form-archivar-curso");
    formArchivar.forEach(form => {
        form.addEventListener("submit", (e) => {
            if (!confirm("¿Está seguro de que desea archivar este curso? Esta acción se puede revertir.")) {
                e.preventDefault();
            }
        });
    });

    document.getElementById('usersToggle').addEventListener('click', function (e) {
        e.preventDefault();

        this.classList.toggle('open');
        document.getElementById('usersSubmenu').classList.toggle('open');
    });

});
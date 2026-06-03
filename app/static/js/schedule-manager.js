document.addEventListener("DOMContentLoaded", function () {
    const diasSemana = [
        { valor: "LUNES", etiqueta: "Lun" },
        { valor: "MARTES", etiqueta: "Mar" },
        { valor: "MIERCOLES", etiqueta: "Mie" },
        { valor: "JUEVES", etiqueta: "Jue" },
        { valor: "VIERNES", etiqueta: "Vie" },
        { valor: "SABADO", etiqueta: "Sab" }
    ];

    const horasDisponibles = [
        "7:00 AM","7:30 AM","8:00 AM","8:30 AM","9:00 AM","9:30 AM",
        "10:00 AM","10:30 AM","11:00 AM","11:30 AM","12:00 PM","12:30 PM",
        "1:00 PM","1:30 PM","2:00 PM","2:30 PM","3:00 PM","3:30 PM",
        "4:00 PM","4:30 PM","5:00 PM","5:30 PM","6:00 PM","6:30 PM",
        "7:00 PM","7:30 PM","8:00 PM","8:30 PM","9:00 PM"
    ];

    const horasEnMinutos = {};
    horasDisponibles.forEach(h => {
        const [time, ampm] = h.split(" ");
        let [hour, min] = time.split(":").map(Number);

        if (ampm === "PM" && hour !== 12) hour += 12;
        if (ampm === "AM" && hour === 12) hour = 0;

        horasEnMinutos[h] = hour * 60 + min;
    });

    const config = window.scheduleConfig || {};
    const form = document.getElementById(config.formId || "form-crear-curso");
    const container = document.getElementById(config.containerId || "horarios-container");
    const btnAdd = document.getElementById("btn-add-schedule");

    if (!container || !btnAdd) return;

    let horarioCount = 0;
    const MAX_HORARIOS = config.maxHorarios || 3;

    function createOptions(selected = "") {
        return horasDisponibles.map(h =>
            `<option value="${h}" ${selected === h ? "selected" : ""}>${h}</option>`
        ).join("");
    }

    function agregarHorario(data = null) {
        if (horarioCount >= MAX_HORARIOS) return;

        const idx = horarioCount++;

        const div = document.createElement("div");
        div.className = "horario-item";

        div.innerHTML = `
            <div class="horario-header">
                <h4>Horario ${idx + 1}</h4>
                <button type="button" class="btn-remove-schedule">Eliminar</button>
            </div>

            <div class="horario-content">
                <div class="dias-grid">
                    ${diasSemana.map(d => `
                        <label class="checkbox-day">
                            <input type="checkbox"
                                   name="horario_${idx}_dias"
                                   value="${d.valor}"
                                   ${data?.dias?.includes(d.valor) ? "checked" : ""}>
                            <span>${d.etiqueta}</span>
                        </label>
                    `).join("")}
                </div>

                <div class="horas-section">
                    <select name="horario_${idx}_inicio" required>
                        <option value="">Inicio</option>
                        ${createOptions(data?.inicio)}
                    </select>

                    <select name="horario_${idx}_fin" required>
                        <option value="">Fin</option>
                        ${createOptions(data?.fin)}
                    </select>
                </div>

                <div class="error-message"></div>
            </div>
        `;

        container.appendChild(div);

        div.querySelector(".btn-remove-schedule").onclick = () => {
            div.remove();
            renumerar();
            validarSolapamientos();
        };

        div.querySelectorAll("input,select").forEach(el => {
            el.addEventListener("change", validarSolapamientos);
        });
    }

    function renumerar() {
        const items = container.querySelectorAll(".horario-item");
        horarioCount = items.length;

        items.forEach((item, idx) => {
            item.querySelector("h4").textContent = `Horario ${idx + 1}`;

            item.querySelectorAll("input[type=checkbox]").forEach(cb => {
                cb.name = `horario_${idx}_dias`;
            });

            item.querySelectorAll("select")[0].name = `horario_${idx}_inicio`;
            item.querySelectorAll("select")[1].name = `horario_${idx}_fin`;
        });
    }

    function validarSolapamientos() {
        const items = [...container.querySelectorAll(".horario-item")];
        let valido = true;

        items.forEach(i => {
            i.querySelector(".error-message").textContent = "";
        });

        const horarios = items.map((item, idx) => ({
            idx,
            dias: [...item.querySelectorAll(`input[name="horario_${idx}_dias"]:checked`)]
                .map(x => x.value),
            inicio: item.querySelector(`[name="horario_${idx}_inicio"]`).value,
            fin: item.querySelector(`[name="horario_${idx}_fin"]`).value,
            el: item
        }));

        for (let i = 0; i < horarios.length; i++) {
            for (let j = i + 1; j < horarios.length; j++) {
                const a = horarios[i];
                const b = horarios[j];

                const diasComun = a.dias.filter(d => b.dias.includes(d));

                if (!diasComun.length) continue;
                if (!a.inicio || !a.fin || !b.inicio || !b.fin) continue;

                const overlap =
                    horasEnMinutos[a.inicio] < horasEnMinutos[b.fin] &&
                    horasEnMinutos[b.inicio] < horasEnMinutos[a.fin];

                if (overlap) {
                    const msg = `Empalme en ${diasComun.join(", ")}`;
                    a.el.querySelector(".error-message").textContent = msg;
                    b.el.querySelector(".error-message").textContent = msg;
                    valido = false;
                }
            }
        }

        return valido;
    }

    btnAdd.onclick = e => {
        e.preventDefault();
        agregarHorario();
    };

    if (window.initialHorarios?.length) {
        window.initialHorarios.forEach(h => agregarHorario(h));
    }

    form?.addEventListener("submit", e => {
        if (!validarSolapamientos()) e.preventDefault();
    });
});
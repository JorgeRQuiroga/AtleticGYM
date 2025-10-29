// Filtro en tiempo real
document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById("buscadorUsuarios");
    const tabla = document.getElementById("tablaUsuarios").getElementsByTagName("tbody")[0];

    if (input) {
        input.addEventListener("keyup", function () {
            const filtro = this.value.toLowerCase().trim();
            const filas = tabla.getElementsByTagName("tr");

            for (let fila of filas) {
                const celdas = fila.getElementsByTagName("td");
                let coincide = false;

                for (let celda of celdas) {
                    if (celda.textContent.toLowerCase().includes(filtro)) {
                        coincide = true;
                        break;
                    }
                }

                fila.style.display = coincide ? "" : "none";
            }
        });
    }

    // Confirmación al eliminar
    document.querySelectorAll('.btn-eliminar').forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            let form = this.closest('form');
            Swal.fire({
                title: '¿Eliminar usuario?',
                text: 'Esta acción no se puede deshacer.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#28a745',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();
                }
            });
        });
    });
});

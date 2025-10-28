// arqueo.js

// Variables globales
let currentPage = 1;
let recordsPerPage = 10;
let filteredData = [];
let allData = [];

// Event Listeners
function initializeEventListeners() {
    // Filtros
    document.getElementById('btn-aplicar-filtros').addEventListener('click', applyFilters);
    document.getElementById('btn-limpiar-filtros').addEventListener('click', clearFilters);
    
    // Registros por página
    document.getElementById('select-per-page').addEventListener('change', function() {
        recordsPerPage = parseInt(this.value);
        currentPage = 1;
        renderTable();
    });
}

// Cargar datos
function loadData() {
    // Usamos los datos proporcionados por Django a través de la plantilla
    allData = arqueosDataFromDjango;
    filteredData = [...allData];
    renderTable();
}

// Aplicar filtros (lógica de ejemplo, se puede expandir)
function applyFilters() {
    const usuarioFilter = document.getElementById('filter-usuario').value;
    const fechaDesde = document.getElementById('filter-fecha-desde').value;
    const fechaHasta = document.getElementById('filter-fecha-hasta').value;

    filteredData = allData.filter(arqueo => {
        // Filtro por usuario
        if (usuarioFilter && arqueo.usuario !== usuarioFilter) {
            return false;
        }

        // Filtro por fecha (usando la fecha de cierre)
        if (fechaDesde || fechaHasta) {
            const arqueoFecha = convertirFecha(arqueo.fecha_cierre);

            if (fechaDesde) {
                const desde = new Date(fechaDesde);
                desde.setHours(0, 0, 0, 0);
                if (arqueoFecha < desde) return false;
            }

            if (fechaHasta) {
                const hasta = new Date(fechaHasta);
                hasta.setHours(23, 59, 59, 999);
                if (arqueoFecha > hasta) return false;
            }
        }

        return true;
    });

    currentPage = 1;
    renderTable();
}

// Convertir fecha del formato dd/mm/yyyy a objeto Date
function convertirFecha(fechaStr) {
    if (!fechaStr || fechaStr === 'N/A') return null;
    const [fecha, hora] = fechaStr.split(' ');
    const [dia, mes, año] = fecha.split('/');
    return new Date(año, mes - 1, dia);
}

// Limpiar filtros
function clearFilters() {
    document.getElementById('filter-usuario').value = '';
    document.getElementById('filter-fecha-desde').value = '';
    document.getElementById('filter-fecha-hasta').value = '';

    filteredData = [...allData];
    currentPage = 1;
    renderTable();
}

// Renderizar tabla
function renderTable() {
    const start = (currentPage - 1) * recordsPerPage;
    const end = start + recordsPerPage;
    const pageData = filteredData.slice(start, end);

    const tbody = document.getElementById('tabla-arqueo-body');

    if (pageData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 40px; color: #999;">No se encontraron registros</td></tr>';
    } else {
        tbody.innerHTML = pageData.map((arqueo, index) => `
            <tr data-id="${arqueo.id}">
                <td>${start + index + 1}</td>
                <td>${arqueo.usuario}</td>
                <td>${arqueo.fecha_apertura}</td>
                <td>$${formatearPrecio(arqueo.valor_apertura)}</td>
                <td>${arqueo.fecha_cierre}</td>
                <td>$${formatearPrecio(arqueo.valor_cierre)}</td>
                <td>$${formatearPrecio(arqueo.monto_contado)}</td>
                <td class="diferencia ${arqueo.diferencia < 0 ? 'negativa' : (arqueo.diferencia > 0 ? 'positiva' : '')}">
                    $${formatearPrecio(arqueo.diferencia)}
                </td>
                <td>
                    <span class="badge ${arqueo.estado === 'Cerrada' ? 'bg-secondary' : 'bg-success'}">
                        ${arqueo.estado}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-info" onclick="verDetalleArqueo(${arqueo.id})">
                        Ver
                    </button>
                </td>
            </tr>
        `).join('');
    }

    updateRecordsInfo();
    renderPagination();
}

// Formatear precio
function formatearPrecio(precio) {
    return precio.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Actualizar información de registros
function updateRecordsInfo() {
    const start = (currentPage - 1) * recordsPerPage + 1;
    const end = Math.min(start + recordsPerPage - 1, filteredData.length);
    const total = filteredData.length;

    document.getElementById('records-count').textContent =
        total > 0 ? `Mostrando ${start} a ${end} de ${total} cierres` : 'Mostrando 0 de 0 cierres';
}

// Renderizar paginación
function renderPagination() {
    const totalPages = Math.ceil(filteredData.length / recordsPerPage);
    const pagination = document.getElementById('pagination');

    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let html = '';
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">Anterior</button>`;

    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `<button class="${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += `<button disabled>...</button>`;
        }
    }

    html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">Siguiente</button>`;
    pagination.innerHTML = html;
}

// Cambiar página
function changePage(page) {
    if (page < 1 || page > Math.ceil(filteredData.length / recordsPerPage)) return;
    currentPage = page;
    renderTable();
}

// Ver detalle (función placeholder, se puede implementar la lógica del modal)
function verDetalleArqueo(id) {
    const arqueo = allData.find(a => a.id === id);
    if (arqueo) {
        alert(`Detalle del Arqueo ID: ${id}\nUsuario: ${arqueo.usuario}\nCierre: ${arqueo.fecha_cierre}\nValor: $${arqueo.valor_cierre}`);
        // Aquí iría la lógica para llenar y mostrar el modal
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadData();
});
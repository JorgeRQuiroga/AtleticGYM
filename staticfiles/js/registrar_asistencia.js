document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form[method="post"]');
  if (!form) return;

  const dniInput = document.querySelector('#id_dni') || document.querySelector('input[name="dni"]');
  const card = document.querySelector('.card');
  const submitBtn = form.querySelector('button[type="submit"]');

  let submitting = false;

  async function mostrarSwal(tipo, titulo, mensaje, timeout = 3000) {
    const opts = {
      title: titulo,
      html: `<p style="margin:0.25rem 0">${mensaje}</p>`,
      icon: tipo,
      showConfirmButton: false,
      timer: timeout,
      backdrop: 'rgba(0,0,0,0.6)'
    };
    await Swal.fire(opts);
  }

  function setDisabled(state) {
    submitting = state;
    if (submitBtn) submitBtn.disabled = state;
    if (dniInput) dniInput.disabled = state;
  }

  function aplicarFocus() {
    if (dniInput) {
      dniInput.focus();
      dniInput.select();
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (submitting) return;

    const dni = dniInput ? dniInput.value.trim() : '';
    if (!dni) {
      await mostrarSwal('warning', 'DNI vacío', 'Por favor ingresa un DNI.');
      aplicarFocus();
      return;
    }

    setDisabled(true);

    // Mostrar loader visual en el botón
    const originalBtnHtml = submitBtn ? submitBtn.innerHTML : null;
    if (submitBtn) submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registrando...`;

    try {
      const action = form.action || window.location.href;
      const formData = new FormData();
      // si el campo tiene name distinto, intentamos ambos
      if (dniInput && dniInput.name) formData.append(dniInput.name, dni);
      else formData.append('dni', dni);
      const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
      if (csrfToken) formData.append('csrfmiddlewaretoken', csrfToken.value);

      const resp = await fetch(action, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
      });

      const text = await resp.text();

      // Parsear respuesta HTML y buscar señales de resultado
      const parser = new DOMParser();
      const doc = parser.parseFromString(text, 'text/html');

      // 1) Buscar mensajes tipo alert-success / alert-warning / alert-error
      const alertEl = doc.querySelector('.alert');
      const clienteCard = doc.querySelector('.text-center.mb-3') || doc.querySelector('.cliente-info') || null;

      if (alertEl) {
        const classes = (alertEl.className || '').toLowerCase();
        const messageText = alertEl.textContent.trim();

        if (classes.includes('alert-success')) {
          // actualizar la card con el HTML retornado para mostrar info del cliente/usuario
          if (card) {
            // sustituir el contenido interno de .card por el nuevo que haya devuelto el servidor
            const nuevoHtml = doc.querySelector('.card') ? doc.querySelector('.card').innerHTML : card.innerHTML;
            card.innerHTML = nuevoHtml;
          }
          await mostrarSwal('success', 'Asistencia registrada', messageText, 2200);
          // mantener foco en input para nuevas registraciones (si existe)
          aplicarFocus();
        } else if (classes.includes('alert-warning')) {
          await mostrarSwal('warning', 'Atención', messageText, 2600);
          if (card) {
            const nuevoHtml = doc.querySelector('.card') ? doc.querySelector('.card').innerHTML : card.innerHTML;
            card.innerHTML = nuevoHtml;
          }
          aplicarFocus();
        } else if (classes.includes('alert-danger') || classes.includes('alert-error') || classes.includes('alert-secondary')) {
          await mostrarSwal('error', 'Error', messageText, 3000);
          aplicarFocus();
        } else {
          // mensaje genérico
          await mostrarSwal('info', 'Resultado', messageText, 2200);
          aplicarFocus();
        }
      } else if (clienteCard) {
        // si no hay .alert pero sí info de cliente, reemplazamos y mostramos éxito
        if (card) {
          const nuevoHtml = doc.querySelector('.card') ? doc.querySelector('.card').innerHTML : card.innerHTML;
          card.innerHTML = nuevoHtml;
        }
        await mostrarSwal('success', 'Asistencia registrada', 'Registro completado.', 2000);
        aplicarFocus();
      } else {
        // fallback: no se encontró estructura esperada, mostramos contenido crudo como info
        await mostrarSwal('info', 'Respuesta', 'Operación completada. Revisa la pantalla.', 2000);
        if (card && doc.querySelector('.card')) card.innerHTML = doc.querySelector('.card').innerHTML;
        aplicarFocus();
      }

    } catch (err) {
      console.error('Error registrar asistencia:', err);
      await mostrarSwal('error', 'Error', 'No se pudo procesar la solicitud. Reintenta.');
      aplicarFocus();
    } finally {
      setDisabled(false);
      if (submitBtn && originalBtnHtml) submitBtn.innerHTML = originalBtnHtml;
    }
  });
});
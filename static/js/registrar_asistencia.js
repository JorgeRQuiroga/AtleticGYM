document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form[method="post"]');
  if (!form) return;

  const dniInput = document.querySelector('#id_dni') || document.querySelector('input[name="dni"]');
  const submitBtn = form.querySelector('button[type="submit"]');
  const resultado = document.getElementById('resultado');

  let submitting = false;

  async function mostrarSwal(tipo, titulo, mensaje, timeout = 2500) {
    await Swal.fire({
      title: titulo,
      html: `<p style="margin:0.25rem 0">${mensaje}</p>`,
      icon: tipo,
      showConfirmButton: false,
      timer: timeout,
      backdrop: 'rgba(0,0,0,0.6)'
    });
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

    const originalBtnHtml = submitBtn ? submitBtn.innerHTML : null;
    if (submitBtn) {
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status"></span> Registrando...`;
    }

    try {
      const action = form.action || window.location.href;
      const formData = new FormData(form);

      const resp = await fetch(action, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
      });

      const text = await resp.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(text, 'text/html');

      // Buscar alertas en la respuesta
      const alertEl = doc.querySelector('.alert');
      if (alertEl) {
        const classes = (alertEl.className || '').toLowerCase();
        const messageText = alertEl.textContent.trim();

        if (classes.includes('alert-success')) {
          await mostrarSwal('success', 'Asistencia registrada', messageText);
        } else if (classes.includes('alert-warning')) {
          await mostrarSwal('warning', 'Atención', messageText);
        } else if (classes.includes('alert-danger') || classes.includes('alert-error')) {
          await mostrarSwal('error', 'Error', messageText);
        } else {
          await mostrarSwal('info', 'Resultado', messageText);
        }
      } else {
        await mostrarSwal('success', 'Asistencia registrada', 'Registro completado.');
      }


      form.reset();
      aplicarFocus();

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

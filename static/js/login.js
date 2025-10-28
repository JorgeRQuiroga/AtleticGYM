document.addEventListener('DOMContentLoaded', function () {
    const flag = document.getElementById('login-success-flag');
    const successAlert = document.querySelector('.alert-success');

    // Solo dispara en login exitoso (flag presente) y con mensaje success
    if (flag && successAlert) {
        const redirectUrl = flag.getAttribute('data-redirect-url') || '/usuarios/home/';

        Swal.fire({
            title: '¡Bienvenido a ATLETIX GYM!',
            html: `<h3 class="text-warning">${successAlert.textContent.trim()}</h3>
                   <p class="mt-2">Hoy es un gran día para entrenar 💪</p>`,
            icon: 'success',
            showConfirmButton: false,
            allowOutsideClick: false,
            allowEscapeKey: false,
            timer: 3500,
            backdrop: `
                rgba(0,0,0,0.85)
                url("/static/img/login_fondo.jpg")
                center/cover
                no-repeat
            `,
            customClass: { popup: 'swal2-show fs-3 p-4 rounded-4' }
        }).then(() => {
            window.location.href = redirectUrl;
        });
    }
});
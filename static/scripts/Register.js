async function Register() {
    const data = {
        username: $('#txt_username').val(),
        password: $('#txt_password').val(),
        confirm_password: $('#txt_confirm_password').val()
    };
    const resp = await tools.PostBack('/Register', data);
    if (resp.status === 1) {
        notification.error(resp.msg);
        return;
    }
    location.href = resp.redirect;
}

async function EnterEvent() {
    const txt_username = $('#txt_username');
    const txt_password = $('#txt_password');
    const txt_confirm_password = $('#txt_confirm_password');
    if (txt_username.val() == '') {
        txt_username.focus();
        return;
    }
    if (txt_password.val() == '') {
        txt_password.focus();
        return;
    }
    if (txt_confirm_password.val() == '') {
        txt_confirm_password.focus();
        return;
    }
    if (txt_password.val() != txt_confirm_password.val()) {
        notification.error("Las contraseñas no coinciden");
        return;
    }
    Register();
}

async function Cargar() {
    while (true) {
        try {
            $('#btn_register').click(Register);
            tools.Enter('#txt_username', EnterEvent);
            tools.Enter('#txt_password', EnterEvent);
            tools.Enter('#txt_confirm_password', EnterEvent);
            break;
        } catch (error) {
            console.log(error);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }
}

$(() => {
    Cargar();
});
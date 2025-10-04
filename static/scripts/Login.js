async function Login() {
    const data = {
        username: $('#txt_username').val(),
        password: $('#txt_password').val()
    };
    const resp = await tools.PostBack('/Login', data);
    if (resp.status === 1) {
        notification.error(resp.msg);
        return;
    }
    location.href = resp.redirect;
}

async function EnterEvent() {
    if ($('#txt_username').val() == '') {
        $('#txt_username').focus();
        return;
    }
    if ($('#txt_password').val() == '') {
        $('#txt_password').focus();
        return;
    }
    Login();
}

async function Cargar() {
    while (true) {
        try {
            $('#btn_login').click(Login);
            tools.Enter('#txt_username', EnterEvent);
            tools.Enter('#txt_password', EnterEvent);
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
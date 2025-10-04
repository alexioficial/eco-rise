const SecurityCheck = async () => {
    const data = {
        const_iduser: const_iduser,
        input_iduser: $('#input_iduser').val()
    };
    const resp = await tools.PostBack('/SecurityCheck', data);
    if (resp.status == 1) {
        notification.error(resp.msg);
        return;
    }
}

setInterval(() => {
    SecurityCheck();
}, 60000);
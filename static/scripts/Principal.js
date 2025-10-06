const getCookie = (name) => {
    const nameEQ = name + '=';
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return '';
};

async function Calculate(data) {
    const resp = await tools.PostBack('/Calculate', data);
    if (resp.status === 1) {
        notification.error(resp.msg);
        return;
    }
    console.log(resp)

    // Fill fields with data calculated by Gemini
    if (resp.temperatura_suelo) {
        $('#txt_temperatura_suelo').val(resp.temperatura_suelo);
    }
    if (resp.demanda_producto) {
        $('#txt_demanda_producto').val(resp.demanda_producto);
    }
    if (resp.probabilidad_lluvia) {
        $('#txt_probabilidad_lluvia').val(resp.probabilidad_lluvia);
    }

    // If there's a redirect, use it
    if (resp.redirect) {
        location.href = resp.redirect;
    }
}

async function ClickCultivos() {
    $('#img_cultivos').click(e => {
        var element = $(`#${e.target.id}`);
        const crop = element.attr('alt');
        switch (crop) {
            case 'tierra_sola':
                element.attr('src', '/static/imgs/cultivos_1.png');
                element.attr('alt', 'cultivos_1');
                break;
            case 'cultivos_1':
                element.attr('src', '/static/imgs/cultivos_2.png');
                element.attr('alt', 'cultivos_2');
                break;
            case 'cultivos_2':
                element.attr('src', '/static/imgs/lechuga.png');
                element.attr('alt', 'lechuga');
                break;
            case 'lechuga':
                element.attr('src', '/static/imgs/tomate.png');
                element.attr('alt', 'tomate');
                break;
            case 'tomate':
                element.attr('src', '/static/imgs/maiz.png');
                element.attr('alt', 'maiz');
                break;
            case 'maiz':
                element.attr('src', '/static/imgs/tierra_sola.png');
                element.attr('alt', 'tierra_sola');
                break;
        }
    });
}

async function SetTodayDate() {
    const today = new Date();

    const year = today.getFullYear();
    var month = today.getMonth() + 1;
    let day = today.getDate();

    if (month < 10) {
        month = '0' + month;
    }
    if (day < 10) {
        day = '0' + day;
    }

    const formattedDate = `${year}-${month}-${day}`;
    $("#txt_fecha").val(formattedDate);
}

async function Load() {
    while (true) {
        try {
            const width = parseFloat(getCookie('vi_ancho')) || null;
            const height = parseFloat(getCookie('vi_alto')) || null;
            const plantType = getCookie('vi_tipoPlanta') || '';
            const lat = parseFloat(getCookie('vi_lat')) || null;
            const lng = parseFloat(getCookie('vi_lng')) || null;

            // await Calculate({
            //     ancho: width,
            //     alto: height,
            //     tipo_planta: plantType,
            //     lat: lat,
            //     lng: lng
            // });
            ClickCultivos();
            SetTodayDate();

            break;
        } catch (error) {
            console.log(error);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }
}

$(() => {
    Load();
});

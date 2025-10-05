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

    // Llenar los campos con los datos calculados por Gemini
    if (resp.temperatura_suelo) {
        $('#txt_temperatura_suelo').val(resp.temperatura_suelo);
    }
    if (resp.demanda_producto) {
        $('#txt_demanda_producto').val(resp.demanda_producto);
    }
    if (resp.probabilidad_lluvia) {
        $('#txt_probabilidad_lluvia').val(resp.probabilidad_lluvia);
    }

    // Si hay redirect, usarlo
    if (resp.redirect) {
        location.href = resp.redirect;
    }
}

async function Cargar() {
    while (true) {
        try {
            const ancho = parseFloat(getCookie('vi_ancho')) || null;
            const alto = parseFloat(getCookie('vi_alto')) || null;
            const tipoPlanta = getCookie('vi_tipoPlanta') || '';
            const lat = parseFloat(getCookie('vi_lat')) || null;
            const lng = parseFloat(getCookie('vi_lng')) || null;

            await Calculate({
                ancho: ancho,
                alto: alto,
                tipo_planta: tipoPlanta,
                lat: lat,
                lng: lng
            });

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

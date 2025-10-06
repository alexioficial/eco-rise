async function Calculate() {
    const resp = await tools.PostBack('/Calculate', {});
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

// async function ClickCultivos() {
//     $('#img_cultivos').click(e => {
//         var element = $(`#${e.target.id}`);
//         const crop = element.attr('alt');
//         switch (crop) {
//             case 'tierra_sola':
//                 element.attr('src', '/static/imgs/cultivos_1.png');
//                 element.attr('alt', 'cultivos_1');
//                 break;
//             case 'cultivos_1':
//                 element.attr('src', '/static/imgs/cultivos_2.png');
//                 element.attr('alt', 'cultivos_2');
//                 break;
//             case 'cultivos_2':
//                 element.attr('src', '/static/imgs/lechuga.png');
//                 element.attr('alt', 'lechuga');
//                 break;
//             case 'lechuga':
//                 element.attr('src', '/static/imgs/tomate.png');
//                 element.attr('alt', 'tomate');
//                 break;
//             case 'tomate':
//                 element.attr('src', '/static/imgs/maiz.png');
//                 element.attr('alt', 'maiz');
//                 break;
//             case 'maiz':
//                 element.attr('src', '/static/imgs/tierra_sola.png');
//                 element.attr('alt', 'tierra_sola');
//                 break;
//         }
//     });
// }

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
    // ClickCultivos();
    SetTodayDate();
    await Calculate();
}

$(() => {
    Load();
});

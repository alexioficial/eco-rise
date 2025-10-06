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
        $('#txt_probabilidad_lluvia').val(resp.probabilidad_lluvia + '%');
    }
    if (resp.efectividad_cultivo) {
        $('.porcentaje_efectividad').text(resp.efectividad_cultivo + '%');
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

async function GetAdvice() {
    // Show modal with loading state
    const modal = new bootstrap.Modal(document.getElementById('adviceModal'));
    modal.show();

    // Reset to loading state
    $('#adviceContent').html(`
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">Analyzing your crop data...</p>
        </div>
    `);

    try {
        const resp = await tools.PostBack('/GetAdvice', {});

        if (resp.status === 1) {
            $('#adviceContent').html(`
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle"></i> ${resp.msg}
                </div>
            `);
            return;
        }

        // Display advice
        $('#adviceContent').html(`
            <div class="text-start w-100">
                <p class="mb-0" style="line-height: 1.6;">${resp.advice}</p>
            </div>
        `);

    } catch (error) {
        console.error('Error getting advice:', error);
        $('#adviceContent').html(`
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle"></i> Error getting advice. Please try again.
            </div>
        `);
    }
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
    // ClickCultivos();
    SetTodayDate();
    await Calculate();
}

$(() => {
    Load();
});

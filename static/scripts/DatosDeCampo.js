async function saveFieldData() {
    const data = {
        water_ph: $('#txt_ph_agua').val(),
        water_conductivity: $('#txt_conductividad_agua').val(),
        soil_salinity: $('#txt_salinidad_tierra').val(),
        soil_moisture: $('#txt_humedad_tierra').val()
    };
    
    try {
        const resp = await tools.PostBack('/SaveFieldData', data);
        if (resp.status === 0) {
            notification.success('Field data saved successfully');
            setTimeout(() => {
                window.location.href = '/Principal';
            }, 500);
        } else {
            notification.error(resp.msg || 'Error saving data');
        }
    } catch (error) {
        console.error('Error saving field data:', error);
        notification.error('Error saving data');
    }
}

// Data is already loaded from backend and populated in HTML
$(() => {
    console.log('DatosDeCampo page loaded');
    // Add save button event listener
    $('#btn-save-field-data').click(saveFieldData);
});

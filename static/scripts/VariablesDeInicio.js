async function Cargar() {
    while (true) {
        try {
            
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

const tools = {
    PostBack: async (route, data, headers = {}) => {
        data['_id'] = window._id || '';
        return new Promise((resolve, reject) => {
            $.ajax({
                type: "POST",
                url: route,
                data: JSON.stringify(data),
                contentType: "application/json",
                dataType: "json",
                headers: headers,
                success: resp => {
                    if (resp.redirect__ != undefined) {
                        window.location.href = resp.redirect__;
                    } else {
                        resolve(resp);
                    }
                },
                error: (xhr, status, error) => {
                    reject(error);
                }
            });
        });
    },
    Enter: (queryselector, callback) => {
        $(queryselector).keyup(e => {
            if (e.key === 'Enter') {
                callback();
            }
        });
    },
    OpenModal: (querySelector, focus) => {
        var element = document.querySelector(querySelector);
        const modal = new bootstrap.Modal(element);
        modal.show();
        $(focus).focus();
    },
    CloseModal: (querySelector) => {
        var element = document.querySelector(querySelector);
        const modal = bootstrap.Modal.getInstance(element);
        if (modal) {
            modal.hide();
        }
    },
    GetData: (idform = "Form") => {
        const root = document.getElementById(idform);
        const data = {};
        if (!root) return data;

        const controls = root.querySelectorAll('input, select');
        controls.forEach(el => {
            const id = el.id || el.getAttribute('id');
            if (!id) return;

            let value;
            if (el.tagName.toLowerCase() === 'input') {
                const type = (el.type || '').toLowerCase();
                if (type === 'checkbox') {
                    value = el.checked;
                } else if (type === 'radio') {
                    if (!el.checked) return; // only take the selected radio
                    value = el.value;
                } else {
                    value = el.value;
                }
            } else {
                // select
                value = el.value;
            }

            data[id] = value;
        });

        return data;
    }
};

const notification = {
    init: function() {
        if (!document.getElementById('toast-container-main')) {
            const container = `
                <div id="toast-container-main" class="toast-container position-fixed top-0 end-0 p-2">
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', container);
        }
    },
    success: function (message) {
        this.init();
        const toastId = 'toast-' + Date.now();
        const html = `
            <div id="${toastId}" class="toast align-items-center text-white bg-success border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>`;
        document.getElementById('toast-container-main').insertAdjacentHTML('beforeend', html);
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 3000 });
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    },
    error: function (message) {
        this.init();
        const toastId = 'toast-' + Date.now();
        const html = `
            <div id="${toastId}" class="toast align-items-center text-white bg-danger border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>`;
        document.getElementById('toast-container-main').insertAdjacentHTML('beforeend', html);
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 3000 });
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    },
    warning: function (message) {
        this.init();
        const toastId = 'toast-' + Date.now();
        const html = `
            <div id="${toastId}" class="toast align-items-center text-dark bg-warning border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>`;
        document.getElementById('toast-container-main').insertAdjacentHTML('beforeend', html);
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 3000 });
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    },
    info: function (message) {
        this.init();
        const toastId = 'toast-' + Date.now();
        const html = `
            <div id="${toastId}" class="toast align-items-center text-white bg-info border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>`;
        document.getElementById('toast-container-main').insertAdjacentHTML('beforeend', html);
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 3000 });
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }
}
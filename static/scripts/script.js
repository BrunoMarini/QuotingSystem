var SELECTED_QUOTATION = -1;
var SERVICES = {};
var CURRENT_PRICE = 0;

/**
 * Function responsible for loading open quotaitons
 */
window.onload = function() {
    const data = {
        status: 'open'
    };

    fetch('/load_quotations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)})
        .then(response => response.json())
        .then(data => {
            if (data.status != 'Ok') {
                // TODO
            }

            const serviceList = document.getElementById('serviceList');
            data.quotations.forEach(service => {
                console.log(service);
                const listItem = document.createElement('li');
                listItem.id = service.id;
                listItem.onclick = function() {
                    onQuotationSelected(service.id, service.name);
                };

                const itemHeader = document.createElement('div');
                itemHeader.className = 'item-header';
                itemHeader.textContent = service.name;

                const itemDetailsPrice = document.createElement('div');
                itemDetailsPrice.id = `price_${service.id}`;
                itemDetailsPrice.className = 'item-details';
                itemDetailsPrice.textContent = `Orçamento Atual: R$ ${service.total_price.toFixed(2)}`;

                const itemDetailsCreated = document.createElement('div');
                itemDetailsCreated.className = 'item-details';
                itemDetailsCreated.textContent = `Criado em: ${service.created_at}`;

                listItem.appendChild(itemHeader);
                listItem.appendChild(itemDetailsPrice);
                listItem.appendChild(itemDetailsCreated);

                serviceList.appendChild(listItem);
            });
        }).catch(error => {
            console.log("Error: " + error);
            alert("Falha ao comunicar com o servidor");
        });
};

/**
 * Function to handle Quotation selection. It will load all QuotationItem
 * for the respective Quotation id
 *
 * @param {*} id
 * @param {*} name
 */
function onQuotationSelected(id, name) {
    console.log("onQuotationSelected: ID = " + id + ", NAME = " + name);
    document.getElementById("client_name").innerHTML = name;

    // Highlighting selected quotation
    if (SELECTED_QUOTATION > 0) {
        document.getElementById(SELECTED_QUOTATION).style.backgroundColor = "antiquewhite";
    }
    document.getElementById(id).style.backgroundColor = "lightblue";
    SELECTED_QUOTATION = id;

    updateItemsTable();
}

/**
 * Auxiliar function to delete QuotationItem and remove row in case of success
 *
 * @param {*} item_id
 * @param {*} table_row
 */
function deleteTableEntry(item_id, table_row) {
    console.log("deleteTableEntry: " + item_id)
    if (confirm("Você tem certeza que deseja deletar esse Serviço?")) {
        const quotation_item = {
            item_id: item_id,
            quotation_id: SELECTED_QUOTATION
        };
        fetch('/delete_quotation_item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(quotation_item)})
            .then(response => response.json())
            .then(data => {
                console.log(data.status);
                if (data.status == 'Ok') {
                    table_row.remove();
                    updateQuotationPrice(data.total_price);
                }
            });
    }
}

/**
 * Function to open for and register new services for quotation
 */
function openForm() {
    if (SELECTED_QUOTATION < 0) {
        alert("Nenhum ordem de serviço selecionada!");
        return;
    }

    fetch('/get_services', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }})
        .then(response => response.json())
        .then(data => {
            if (data.status != 'Ok') {
                // TODO
            }

            if (data.services.length == 0) {
                // TODO
            }

            SERVICES = data.services;

            select_component = document.getElementById("selected_service");

            // Adding default option
            new_option = document.createElement("option");
            new_option.value = -1;
            new_option.innerHTML = "Selecione o serviço";
            select_component.appendChild(new_option);

            data.services.forEach(element => {
                new_option = document.createElement("option");
                new_option.value = element.id;
                new_option.innerHTML = element.name;
                select_component.appendChild(new_option);
            });

            document.getElementById("add_service_form").style.display = "block";
        });
}

function closeForm() {
    document.getElementById("quantity").value = "1";
    document.getElementById("selected_service").replaceChildren();
    document.getElementById("add_service_form").style.display = "none";
}

function updatePopup(event) {
    const selected_id = event.target.value;
    const result = SERVICES.some(service => {
        if (service.id == selected_id) {
            CURRENT_PRICE = service.price;
            updatePopupPrice();
            return true;
        }
    });

    if (!result) {
        CURRENT_PRICE = 0;
        updatePopupPrice();
    }
}

function updatePopupPrice() {
    const quantity = document.getElementById("quantity").value;
    document.getElementById("unit_price").textContent = "R$ " + CURRENT_PRICE.toFixed(2);
    document.getElementById("total_price").textContent = "R$ " + (quantity * CURRENT_PRICE).toFixed(2);
}

function addNewService() {
    const product_id = document.getElementById("selected_service").value;
    const quantity = document.getElementById("quantity").value;

    console.log("Adding " + quantity + "x" + product_id + " for " + SELECTED_QUOTATION);

    if (product_id < 0 && quantity < 1) {
        alert("Seleção invalida");
        return;
    }

    const service_to_add = {
        quotation_id: SELECTED_QUOTATION,
        service: +product_id,
        quantity: +quantity
    };

    fetch('/add_service_to_quotation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(service_to_add)})
        .then(response => response.json())
        .then(data => {
            console.log(data.status);
            if (data.status == 'Ok') {
                updateQuotationPrice(data.total_price);
                updateItemsTable();
                closeForm();
                return;
            } else {
                alert("Erro interno");
            }
        });
}

function updateQuotationPrice(price) {
    console.log(price);
    if (SELECTED_QUOTATION > 0) {
        quotation = document.getElementById(`price_${SELECTED_QUOTATION}`);
        quotation.textContent = `Orçamento Atual: R$ ${price.toFixed(2)}`
    }
}

function updateItemsTable() {
    const user_id = {
        id: SELECTED_QUOTATION
    };

    fetch('/load_items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user_id)})
        .then(response => response.json())
        .then(data => {
            var table = document.getElementById("services_table")

            while (table.rows.length > 1) {
                table.deleteRow(1)
            }

            if (data.items.length == 0) {
                // TODO
            } else {
                data.items.forEach(element => {
                    var row = table.insertRow(1);

                    row.insertCell(0).innerHTML = element.service;
                    // TODO: Is it worth to let user increment this quantity directly on table?
                    row.insertCell(1).innerHTML = element.quantity;
                    row.insertCell(2).innerHTML = "R$ " + element.service_price;
                    row.insertCell(3).innerHTML = "R$ " + element.total_price

                    icon_cell = row.insertCell(4)
                    icon_cell.innerHTML = "<img src='../static/images/ic_trash.png' class='table_image'>"
                    icon_cell.addEventListener('click', function() {
                        deleteTableEntry(element.item_id, row);
                    });
                });
            }
        }).catch(error => {
            console.log("Error: " + error);
            alert("Falha ao comunicar com o servidor");
        });
}
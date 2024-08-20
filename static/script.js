function onQuotationSelected(id, name) {
    console.log("onQuotationSelected: ID = " + id + ", NAME = " + name);
    const user_id = {
        id: id,
        name: name
    };

    fetch('/load_quotation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user_id)})
        .then(response => response.json())
        .then(data => {
            var table = document.getElementById("services_table")

            while (table.rows.length > 1) {
                table.deleteRow(1)
            }

            document.getElementById("client_name").innerHTML = data.name

            if (data.items.length == 0) {
                // TODO
            } else {
                data.items.forEach(element => {
                    console.log(element)
                    var row = table.insertRow(1);

                    row.insertCell(0).innerHTML = element.service;
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
        });
}

function deleteTableEntry(item_id, table_row) {
    console.log("deleteTableEntry: " + item_id)
    if (confirm("Você tem certeza que deseja deletar esse Serviço?")) {
        const quotation_item = { id: item_id };
        fetch('/delete_quotation_item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(quotation_item)})
            .then(response => response.json())
            .then(data => {
                console.log(data.status);
                if (data.status == 'Ok') {
                    table_row.remove();
                }
            });
    }
}

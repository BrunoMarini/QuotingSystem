function onQuotationSelected(id, name) {
    console.log("onQuotationSelected: ID = " + id + ", NAME = " + name);
    const user_id = {
        id: id,
        name: name
    };

    fetch('/load_quotation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user_id)
    }).then(response => response.json())
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
                });
            }
        });
}

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
            console.log(data)
            //document.getElementById("content").innerHTML = data.updated_content;
        });


}

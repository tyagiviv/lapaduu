let rowCount = 1; // Counter for rows

function addDescriptionItems() {
    rowCount++; // Increment the row counter

    // Create new row for description
    var newRow = document.createElement('div');
    newRow.className = 'inputfieldStyledescription';

    newRow.innerHTML = `
        <!-- First Row: Titles -->
        <label for="description${rowCount}"><b>Description</b></label>
        <label for="quantity${rowCount}"><b>Quantity / Hr</b></label>
        <label for="price${rowCount}"><b>Price</b></label>
        <label for="discount${rowCount}"><b>Discount %</b></label>
        <label for="total${rowCount}"><b>Total Amount</b></label>

        <!-- First Row: Inputs -->
        <div class="input-row">
            <input type="text" id="description${rowCount}" name="description" list="descriptionList${rowCount}">
            <datalist id="descriptionList${rowCount}">
                <option value="Service A">
                <option value="Service B">
                <option value="Service C">
                <option value="Consulting">
                <option value="Development">
                <option value="Support">
            </datalist>
            <input type="number" id="quantity${rowCount}" name="quantity" onchange="calculateTotal(this)" placeholder="Quantity/Hr">
            <input type="number" id="price${rowCount}" name="price" onchange="calculateTotal(this)" placeholder="Price">
            <input type="number" id="discount${rowCount}" name="discount" onchange="calculateTotal(this)" placeholder="Discount %">
            <input type="number" id="total${rowCount}" name="total" placeholder="Total Amount" readonly>
        </div>
    `;

    // Append the new row to the spDiv
    var myDiv = document.getElementById("spDiv");
    myDiv.appendChild(newRow);
}

function calculateTotal(input) {
    // Find the parent div of the input field
    var parentDiv = input.closest('.inputfieldStyledescription');

    // Get the quantity, price, and discount values from the inputs
    var quantity = parseFloat(parentDiv.querySelector('input[name="quantity"]').value) || 0;
    var price = parseFloat(parentDiv.querySelector('input[name="price"]').value) || 0;
    var discount = parseFloat(parentDiv.querySelector('input[name="discount"]').value) || 0;

    // Calculate total amount
    var totalAmount = (quantity * price) * (1 - discount / 100);

    // Set the total amount in the total input field
    parentDiv.querySelector('input[name="total"]').value = totalAmount.toFixed(2);
}

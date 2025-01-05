let rowCount = 1; // Counter for rows

// Function to add description items dynamically
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

// Function to calculate total for each item based on quantity, price, and discount
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

// Correctly pass the URLs into JavaScript using Django template tags
var generateInvoiceUrl = "{% url 'generate_invoice' %}";  // Correct way to generate the URL
var getNextInvoiceUrl = "{% url 'get_next_invoice_number' %}";  // Correctly inject get_next_invoice_number URL

// Function to fetch the next invoice number from the backend
function fetchNextInvoiceNumber() {
    fetch(getNextInvoiceUrl)  // Use the dynamically generated URL here
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const nextInvoiceNumber = data.next_invoice_number;
                document.getElementById('invoiceNumber').value = nextInvoiceNumber;
            } else {
                alert('Error fetching next invoice number');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error fetching the next invoice number');
        });
}


// Function to create the invoice
function createinvoice() {
    // Collect the basic client info
    var clientEmail = document.getElementById("clientEmail").value;
    var invoiceDate = document.getElementById("invoiceDate").value;
    var clientName = document.getElementById("clientName").value;
    var clientAddress = document.getElementById("clientAddress").value;
    var registrationCode = document.getElementById("registrationCode").value;
    var dueDate = document.getElementById("dueDate").value;

    // Collect description items (dynamically generated rows)
    var descriptions = [];
    var quantities = [];
    var prices = [];
    var discounts = [];
    var totals = [];

    for (let i = 1; i <= rowCount; i++) {
        let description = document.getElementById(`description${i}`).value;
        let quantity = document.getElementById(`quantity${i}`).value;
        let price = document.getElementById(`price${i}`).value;
        let discount = document.getElementById(`discount${i}`).value || "0"; // Default discount to 0 if empty
        let total = document.getElementById(`total${i}`).value;

        // Only collect non-empty rows
        if (description && quantity && price && discount && total) {
            descriptions.push(description);
            quantities.push(quantity);
            prices.push(price);
            discounts.push(discount);
            totals.push(total);
        }
    }

    // Check if at least one item has been added
    if (descriptions.length === 0) {
        alert("Please add at least one description item!");
        return;
    }

    // Make an AJAX request to the server to generate the invoice
    fetch(generateInvoiceUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            clientEmail: clientEmail,
            invoiceDate: invoiceDate,
            clientName: clientName,
            clientAddress: clientAddress,
            registrationCode: registrationCode,
            dueDate: dueDate,
            descriptions: descriptions,
            quantities: quantities,
            prices: prices,
            discounts: discounts,
            totals: totals
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Invoice created successfully! You can download it from: " + data.filename);
            resetForm();
            fetchNextInvoiceNumber();  // Fetch the next invoice number after successful creation
        } else {
            alert("Error: " + data.error);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("There was an error creating the invoice");
    });
}

// Function to reset the form fields
function resetForm() {
    // Reset basic client information fields
    document.getElementById("clientEmail").value = "";
    document.getElementById("clientName").value = "";
    document.getElementById("clientAddress").value = "";
    document.getElementById("registrationCode").value = "";

    // Reset invoice date to today's date
    const today = new Date();
    const todayISO = today.toISOString().split('T')[0];
    const invoiceDateField = document.getElementById("invoiceDate");
    invoiceDateField.value = todayISO;

    // Reset due date to two weeks from today
    const dueDate = new Date();
    dueDate.setDate(today.getDate() + 14);
    const dueDateISO = dueDate.toISOString().split('T')[0];
    const dueDateField = document.getElementById("dueDate");
    dueDateField.value = dueDateISO;

    // Reset description rows
    for (let i = 1; i <= rowCount; i++) {
        document.getElementById(`description${i}`).value = "";
        document.getElementById(`quantity${i}`).value = "";
        document.getElementById(`price${i}`).value = "";
        document.getElementById(`discount${i}`).value = "";
        document.getElementById(`total${i}`).value = "";
    }

    // Optionally, reset the row count if you want to start from the first row
    rowCount = 1;
    document.getElementById("spDiv").innerHTML = ''; // Clears any added rows dynamically

   // Reload the page to refresh everything
    location.reload(); // This reloads the page to reset and fetch the new invoice number

    // Fetch the next invoice number after a short delay to ensure the page is fully loaded
    setTimeout(function() {
        fetchNextInvoiceNumber(); // Fetch the new invoice number
    }, 500);  // Delay in milliseconds, you can adjust this value
}

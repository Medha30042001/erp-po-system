const API_BASE_URL = "http://127.0.0.1:8000";

async function loadPurchaseOrders() {
    const tableBody = document.getElementById("poTableBody");

    try {
        const response = await fetch(`${API_BASE_URL}/purchase-orders`);
        const data = await response.json();

        const orders = data.purchase_orders || [];

        if(orders.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td>No purchase orders found.</td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = "";

        orders.forEach((order) => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${order.reference_no}</td>
                <td>${order.vendor_name}</td>
                <td>${order.total_amount.toFixed(2)}</td>
                <td>${order.status}</td>
                <td>${new Date(order.created_at).toLocaleString()}</td>
            `;

            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error("Error loading purchase orders : ", error);

        tableBody.innerHTML = `
            <tr>
                <td>Failed to load purchase orders.</td>
            </tr>
        `
    }
}

loadPurchaseOrders();
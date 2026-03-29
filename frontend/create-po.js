const API_BASE_URL = "https://erp-po-system-ur32.onrender.com";

const vendorSelect = document.getElementById("vendorSelect");
const itemsContainer = document.getElementById("itemsContainer");
const addRowBtn = document.getElementById("addRowBtn");
const purchaseOrderForm = document.getElementById("purchaseOrderForm");
const messageBox = document.getElementById("messageBox");

let products = [];

async function loadVendors() {
  try {
    const response = await fetch(`${API_BASE_URL}/vendors`);
    const data = await response.json();

    const vendors = data.vendors || [];

    vendorSelect.innerHTML = `<option value="">Select a vendor</option>`;

    vendors.forEach((vendor) => {
      const option = document.createElement("option");
      option.value = vendor.id;
      option.textContent = vendor.name;
      vendorSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Error loading vendors:", error);
    vendorSelect.innerHTML = `<option value="">Failed to load vendors</option>`;
  }
}

async function loadProducts() {
  try {
    const response = await fetch(`${API_BASE_URL}/products`);
    const data = await response.json();
    products = data.products || [];
  } catch (error) {
    console.error("Error loading products:", error);
  }
}

function createProductOptions() {
  let options = `<option value="">Select a product</option>`;

  products.forEach((product) => {
    options += `<option value="${product.id}">${product.name} (₹ ${product.unit_price})</option>`;
  });

  return options;
}

function addItemRow() {
  const row = document.createElement("div");
  row.className = "row g-3 align-items-end mb-3 item-row";

  row.innerHTML = `
    <div class="col-md-6">
      <label class="form-label">Product</label>
      <select class="form-select product-select" required>
        ${createProductOptions()}
      </select>
    </div>

    <div class="col-md-4">
      <label class="form-label">Quantity</label>
      <input type="number" class="form-control quantity-input" min="1" required />
    </div>

    <div class="col-md-2">
      <button type="button" class="btn btn-danger remove-row-btn w-100">Remove</button>
    </div>
  `;

  const removeBtn = row.querySelector(".remove-row-btn");
  removeBtn.addEventListener("click", () => {
    row.remove();
  });

  itemsContainer.appendChild(row);
}

purchaseOrderForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const vendorId = vendorSelect.value;
  const itemRows = document.querySelectorAll(".item-row");

  const items = [];

  itemRows.forEach((row) => {
    const productId = row.querySelector(".product-select").value;
    const quantity = row.querySelector(".quantity-input").value;

    if (productId && quantity) {
      items.push({
        product_id: productId,
        quantity: Number(quantity)
      });
    }
  });

  if (!vendorId) {
    messageBox.innerHTML = `<div class="alert alert-danger">Please select a vendor.</div>`;
    return;
  }

  if (items.length === 0) {
    messageBox.innerHTML = `<div class="alert alert-danger">Please add at least one product row.</div>`;
    return;
  }

  const payload = {
    vendor_id: vendorId,
    items: items
  };

  try {
    const response = await fetch(`${API_BASE_URL}/purchase-orders`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (!response.ok) {
      messageBox.innerHTML = `<div class="alert alert-danger">Failed to create purchase order.</div>`;
      return;
    }

    messageBox.innerHTML = `
      <div class="alert alert-success">
        Purchase order created successfully! <br />
        <strong>Reference No:</strong> ${result.purchase_order.reference_no} <br />
        <strong>Total Amount:</strong> ₹ ${result.purchase_order.total_amount.toFixed(2)}
      </div>
    `;

    purchaseOrderForm.reset();
    itemsContainer.innerHTML = "";
    addItemRow();
  } catch (error) {
    console.error("Error creating purchase order:", error);
    messageBox.innerHTML = `<div class="alert alert-danger">Something went wrong while creating purchase order.</div>`;
  }
});

addRowBtn.addEventListener("click", addItemRow);

async function initPage() {
  await loadVendors();
  await loadProducts();
  addItemRow();
}

initPage();
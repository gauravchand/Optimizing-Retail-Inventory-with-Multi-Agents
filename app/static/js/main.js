// Global variables
const CURRENT_USER = "AkarshanGupta";
const CURRENT_DATETIME = "2025-04-10 15:42:30";
let forecastChart = null;

// Initialize everything when the page loads
document.addEventListener('DOMContentLoaded', async () => {
    // Add toast container to the body if it doesn't exist
    if (!document.querySelector('.toast-container')) {
        document.body.innerHTML += `
            <div class="toast-container position-fixed bottom-0 end-0 p-3"></div>
        `;
    }

    // Initialize all components
    await Promise.all([
        checkInventory(),
        checkAlerts()
    ]);

    // Add store change listener
    document.getElementById('storeSelect').addEventListener('change', async () => {
        await Promise.all([
            checkInventory(),
            checkAlerts()
        ]);
    });
});

// Main inventory functions
async function checkInventory() {
    const store = document.getElementById('storeSelect').value;
    const inventoryData = document.getElementById('inventoryData');

    try {
        inventoryData.innerHTML = `
            <div class="text-center py-4">
                <div class="loading-spinner"></div>
                <p class="text-muted mt-2">Loading inventory...</p>
            </div>
        `;

        const response = await fetch(`/api/inventory/${store}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();

        // Update metrics and display inventory
        updateDashboardMetrics(data);
        displayInventory(data);
    } catch (error) {
        console.error('Error:', error);
        inventoryData.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>Error loading inventory: ${error.message}
            </div>
        `;
    }
}

async function updateInventory() {
    const store = document.getElementById('storeSelect').value;
    const product = document.getElementById('productSelect').value;
    const quantity = parseInt(document.getElementById('quantity').value);

    if (!quantity) {
        showToast('error', 'Please enter a valid quantity');
        return;
    }

    try {
        const response = await fetch(`/api/inventory/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                store_id: store,
                product_id: product,
                quantity: quantity
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        showToast('success', `Inventory updated successfully! New stock level: ${data.new_stock_level}`);
        document.getElementById('quantity').value = ''; // Clear input

        // Refresh data
        await Promise.all([
            checkInventory(),
            checkAlerts(),
            getForecast()
        ]);
    } catch (error) {
        console.error('Error:', error);
        showToast('error', `Error updating inventory: ${error.message}`);
    }
}

// Price update function
async function updatePrice(productId, newPrice) {
    const store = document.getElementById('storeSelect').value;
    try {
        // Show loading state on the button
        const button = document.querySelector(`button[data-product-id="${productId}"]`);
        const originalContent = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
        button.disabled = true;

        const response = await fetch('/api/update-price', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                store_id: store,
                product_id: productId,
                new_price: parseFloat(newPrice)
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        showToast('success', `Price updated to $${parseFloat(newPrice).toFixed(2)} successfully!`);

        // Refresh all relevant displays
        await Promise.all([
            checkInventory(),
            optimizePrices(),
            getForecast()
        ]);
    } catch (error) {
        console.error('Error:', error);
        showToast('error', `Failed to update price: ${error.message}`);
        // Restore button state
        if (button) {
            button.innerHTML = originalContent;
            button.disabled = false;
        }
    }
}

// Forecast functions
async function getForecast() {
    const store = document.getElementById('storeSelect').value;
    const forecastData = document.getElementById('forecastData');

    try {
        forecastData.innerHTML = `
            <div class="text-center py-4">
                <div class="loading-spinner"></div>
                <p class="text-muted mt-2">Generating forecast...</p>
            </div>
        `;

        const response = await fetch(`/api/forecast/${store}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        displayForecast(data);
    } catch (error) {
        console.error('Error:', error);
        forecastData.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>Error generating forecast: ${error.message}
            </div>
        `;
    }
}

// Price optimization functions
async function optimizePrices() {
    const store = document.getElementById('storeSelect').value;
    const container = document.getElementById('priceOptimizationData');

    try {
        container.innerHTML = `
            <div class="text-center py-4">
                <div class="loading-spinner"></div>
                <p class="text-muted mt-2">Optimizing prices...</p>
            </div>
        `;

        const response = await fetch(`/api/price-optimization/${store}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        displayPriceOptimization(data);
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>Error optimizing prices: ${error.message}
            </div>
        `;
    }
}

// Alert functions
async function checkAlerts() {
    const store = document.getElementById('storeSelect').value;
    const container = document.getElementById('alertsData');

    try {
        container.innerHTML = `
            <div class="text-center py-4">
                <div class="loading-spinner"></div>
                <p class="text-muted mt-2">Checking alerts...</p>
            </div>
        `;

        const response = await fetch(`/api/inventory-alerts/${store}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        displayAlerts(data);
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>Error checking alerts: ${error.message}
            </div>
        `;
    }
}

// Display functions
function displayInventory(data) {
    const container = document.getElementById('inventoryData');
    let html = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="mb-0">Store: ${data.store_id}</h6>
            <span class="badge bg-primary">Last updated: ${formatDateTime(data.checked_at)}</span>
        </div>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead class="table-light">
                    <tr>
                        <th>Product</th>
                        <th>Category</th>
                        <th>Stock Level</th>
                        <th>Price</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;

    data.inventory.forEach(item => {
        const statusClass = item.current_stock < item.min_threshold ? 'text-danger' : 'text-success';
        const status = item.current_stock < item.min_threshold ? 'Low Stock' : 'In Stock';

        html += `
            <tr>
                <td>${item.name}</td>
                <td>${item.category}</td>
                <td>${item.current_stock}</td>
                <td>$${item.price.toFixed(2)}</td>
                <td>
                    <span class="badge ${statusClass === 'text-danger' ? 'bg-danger' : 'bg-success'}">
                        ${status}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="quickAdd('${item.product_id}', 10)">
                        <i class="fas fa-plus"></i> Add 10
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
        <div class="text-muted small">
            Managed by: ${data.checked_by}
        </div>
    `;

    container.innerHTML = html;
    updateDashboardMetrics(data);
}

function displayForecast(data) {
    const container = document.getElementById('forecastData');
    const ctx = document.getElementById('forecastChart').getContext('2d');

    // Destroy existing chart if it exists
    if (forecastChart) {
        forecastChart.destroy();
    }

    // Prepare data for chart
    const labels = data.forecast.map(item => item.product_name);
    const currentStock = data.forecast.map(item => item.current_stock);
    const predictedDemand = data.forecast.map(item => item.predicted_demand);

    // Create new chart
    forecastChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Current Stock',
                    data: currentStock,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Predicted Demand',
                    data: predictedDemand,
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Demand Forecast for ${data.store_id}`,
                    font: { size: 16 }
                },
                legend: { position: 'bottom' }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Units'
                    }
                }
            }
        }
    });

    // Display detailed table
    let html = `
        <div class="mt-4">
            <h6>Detailed Forecast</h6>
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Current Stock</th>
                            <th>Predicted Demand</th>
                            <th>Confidence</th>
                            <th>Action Needed</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    data.forecast.forEach(item => {
        const deficit = item.predicted_demand - item.current_stock;
        const actionNeeded = deficit > 0 ?
            `<span class="text-danger">Order ${deficit} units</span>` :
            '<span class="text-success">Stock sufficient</span>';

        html += `
            <tr>
                <td>${item.product_name}</td>
                <td>${item.current_stock}</td>
                <td>${item.predicted_demand}</td>
                <td>${(item.confidence * 100).toFixed(1)}%</td>
                <td>${actionNeeded}</td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
        <div class="text-muted small mt-2">
            Generated: ${formatDateTime(data.generated_at)} by ${data.generated_by}
        </div>
    `;

    container.innerHTML = html;
}

function displayPriceOptimization(data) {
    const container = document.getElementById('priceOptimizationData');
    let html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead class="table-light">
                    <tr>
                        <th>Product</th>
                        <th>Current Price</th>
                        <th>Suggested Price</th>
                        <th>Potential Profit</th>
                        <th>Expected Impact</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
    `;

    data.optimized_prices.forEach(item => {
        const priceChange = ((item.suggested_price - item.current_price) / item.current_price * 100).toFixed(1);
        const changeClass = priceChange >= 0 ? 'text-success' : 'text-danger';
        const changeIcon = priceChange >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';

        html += `
            <tr>
                <td>${item.product_name}</td>
                <td>$${item.current_price.toFixed(2)}</td>
                <td>$${item.suggested_price.toFixed(2)}</td>
                <td>$${item.potential_profit_increase.toFixed(2)}</td>
                <td class="${changeClass}">
                    <i class="fas ${changeIcon}"></i> ${Math.abs(priceChange)}%
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary"
                            onclick="updatePrice('${item.product_id}', ${item.suggested_price.toFixed(2)})"
                            data-product-id="${item.product_id}"
                            data-new-price="${item.suggested_price.toFixed(2)}">
                        Apply
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
        <div class="text-muted small mt-2">
            Analysis generated: ${formatDateTime(data.generated_at)} by ${data.generated_by}
        </div>
    `;

    container.innerHTML = html;
}

function displayAlerts(data) {
    const container = document.getElementById('alertsData');
    let html = '';

    if (data.alerts.length === 0) {
        html = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i> All inventory levels are normal
            </div>
        `;
    } else {
        html = `<div class="alert-list">`;
        data.alerts.forEach(alert => {
            const urgencyClass = alert.urgency === 'HIGH' ? 'bg-danger text-white' : 'bg-warning';
            html += `
                <div class="alert ${urgencyClass} mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                ${alert.product_name}
                            </h6>
                            <div>Current Stock: ${alert.current_stock} (Minimum: ${alert.min_threshold})</div>
                            <div><strong>Urgency: ${alert.urgency}</strong></div>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-light" onclick="orderStock('${alert.product_id}', ${alert.suggested_order})">
                                <i class="fas fa-shopping-cart me-1"></i> Order ${alert.suggested_order} units
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        html += `</div>`;
    }

    html += `
        <div class="text-muted small">
            Last checked: ${formatDateTime(data.generated_at)} by ${data.generated_by}
        </div>
    `;

    container.innerHTML = html;
}

// Utility functions
function formatDateTime(datetime) {
    return new Date(datetime).toLocaleString();
}

function updateDashboardMetrics(data) {
    document.getElementById('totalProducts').textContent = data.inventory.length;
    document.getElementById('lowStockItems').textContent =
        data.inventory.filter(item => item.current_stock < item.min_threshold).length;
    document.getElementById('totalValue').textContent =
        '$' + data.inventory.reduce((sum, item) => sum + (item.current_stock * item.price), 0).toFixed(2);
    document.getElementById('lastUpdate').textContent =
        new Date(data.checked_at).toLocaleTimeString();
}

function showToast(type, message) {
    const toastContainer = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Quick actions
async function quickAdd(productId, quantity) {
    const store = document.getElementById('storeSelect').value;
    try {
        const response = await fetch(`/api/inventory/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                store_id: store,
                product_id: productId,
                quantity: quantity
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        showToast('success', `Added ${quantity} units successfully!`);
        await Promise.all([
            checkInventory(),
            checkAlerts()
        ]);
    } catch (error) {
        console.error('Error:', error);
        showToast('error', `Error adding inventory: ${error.message}`);
    }
}

// Data export
async function exportData() {
    const store = document.getElementById('storeSelect').value;
    try {
        const [inventoryResponse, forecastResponse, alertsResponse] = await Promise.all([
            fetch(`/api/inventory/${store}`),
            fetch(`/api/forecast/${store}`),
            fetch(`/api/inventory-alerts/${store}`)
        ]);

        const [inventory, forecast, alerts] = await Promise.all([
            inventoryResponse.json(),
            forecastResponse.json(),
            alertsResponse.json()
        ]);

        const data = {
            store_id: store,
            exported_at: new Date().toISOString(),
            exported_by: CURRENT_USER,
            inventory: inventory.inventory,
            forecast: forecast.forecast,
            alerts: alerts.alerts
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `inventory-report-${store}-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

        showToast('success', 'Data exported successfully!');
    } catch (error) {
        console.error('Error:', error);
        showToast('error', 'Error exporting data');
    }
}
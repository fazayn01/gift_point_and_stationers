

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const state = {
    user: null,
    selectedRole: null,
    products: [],
    customers: [],
    cart: [],
    linkedCustomer: null,
    exchangeRates: {},
    selectedCurrency: 'EUR',
    recentSales: []
};

document.addEventListener('DOMContentLoaded', () => {

    fetchExchangeRates();
});

async function fetchExchangeRates() {
    try {
        const response = await fetch(`${API_BASE_URL}/exchange-rate`);
        const data = await response.json();
        if (data.success) {
            state.exchangeRates = data.rates;
        }
    } catch (error) {
        console.error('Error fetching exchange rates:', error);

        state.exchangeRates = {
            "USD": 1.08,
            "GBP": 0.85,
            "PKR": 303.00,
            "SAR": 4.05,
            "AED": 3.97
        };
    }
}

function selectRole(role) {
    state.selectedRole = role;

    document.getElementById('role-selection-group').classList.add('hidden');
    const form = document.getElementById('login-form');
    form.classList.remove('hidden');

    const badgeText = role.charAt(0).toUpperCase() + role.slice(1);
    document.getElementById('selected-role-name').innerText = badgeText;

    const userIdInput = document.getElementById('login-user-id');
    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');

    if (role === 'employee') {
        userIdInput.value = '241462';
        usernameInput.value = 'Aruj';
        passwordInput.value = 'aruj123';
    } else if (role === 'admin') {
        userIdInput.value = '1';
        usernameInput.value = 'Admin';
        passwordInput.value = 'admin123';
    } else if (role === 'owner') {
        userIdInput.value = '3';
        usernameInput.value = 'Owner';
        passwordInput.value = 'owner123';
    }
}
function resetRoleSelection() {
    state.selectedRole = null;
    document.getElementById('role-selection-group').classList.remove('hidden');
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('login-error-msg').classList.add('hidden');
}

async function handleLogin(event) {
    event.preventDefault();
    document.getElementById('login-error-msg').classList.add('hidden');

    const userId = document.getElementById('login-user-id').value;
    const name = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const role = state.selectedRole;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userId, name, password, role })
        });

        const data = await response.json();
        if (response.ok && data.success) {
            state.user = data.user;
            enterDashboard();
        } else {
            showLoginError(data.message || 'Login failed.');
        }
    } catch (error) {
        showLoginError('Could not connect to the backend server.');
    }
}
function showLoginError(msg) {
    const errorBanner = document.getElementById('login-error-msg');
    const errorText = document.getElementById('login-error-text');
    errorText.innerText = msg;
    errorBanner.classList.remove('hidden');
}
function enterDashboard() {

    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('dashboard-screen').classList.add('active');

    document.getElementById('display-user-name').innerText = state.user.name;

    const roleLabels = {
        admin: 'System Administrator',
        employee: 'Cashier / Terminal Operator',
        owner: 'Business Owner'
    };
    document.getElementById('display-user-role').innerText = roleLabels[state.user.role];
    document.getElementById('avatar-initials').innerText = state.user.name.charAt(0).toUpperCase();

    document.querySelectorAll('.role-panel').forEach(p => p.classList.add('hidden'));

    if (state.user.role === 'employee') {
        document.getElementById('employee-panel').classList.remove('hidden');
        loadEmployeeView();
    } else if (state.user.role === 'admin') {
        document.getElementById('admin-panel').classList.remove('hidden');
        loadAdminView();
    } else if (state.user.role === 'owner') {
        document.getElementById('owner-panel').classList.remove('hidden');
        loadOwnerView();
    }
}
function handleLogout() {
    state.user = null;
    state.selectedRole = null;
    state.cart = [];
    state.linkedCustomer = null;

    document.getElementById('login-user-id').value = '';
    document.getElementById('login-username').value = '';
    document.getElementById('login-password').value = '';

    document.getElementById('dashboard-screen').classList.remove('active');
    document.getElementById('login-screen').classList.add('active');
    resetRoleSelection();
}

async function loadEmployeeView() {
    state.cart = [];
    state.linkedCustomer = null;
    state.selectedCurrency = 'EUR';
    document.getElementById('currency-convert-selector').value = 'EUR';
    document.getElementById('linked-customer-banner').classList.add('hidden');
    document.getElementById('register-quick-customer').classList.add('hidden');
    document.getElementById('cart-customer-phone-search').value = '';

    await loadCashierProducts();
    updateCartUI();
}
async function loadCashierProducts() {
    const searchVal = document.getElementById('cashier-product-search').value;
    try {
        const response = await fetch(`${API_BASE_URL}/products?q=${encodeURIComponent(searchVal)}`);
        state.products = await response.json();
        renderCatalog();
    } catch (error) {
        console.error('Error fetching catalog:', error);
    }
}
function renderCatalog() {
    const catalogContainer = document.getElementById('cashier-catalog-items');
    catalogContainer.innerHTML = '';

    if (state.products.length === 0) {
        catalogContainer.innerHTML = `<div class="info-text padding-2">No matching products found.</div>`;
        return;
    }

    state.products.forEach(p => {
        const isOutOfStock = p.StockQty <= 0;
        const card = document.createElement('div');
        card.className = 'catalog-card';
        card.innerHTML = `
            <div class="catalog-card-header">
                <h4>${escapeHTML(p.Name)}</h4>
                <p title="${escapeHTML(p.Description || '')}">${escapeHTML(p.Description || 'No description available.')}</p>
            </div>
            <div class="catalog-card-footer">
                <div>
                    <div class="price">€ ${p.Price.toFixed(2)}</div>
                    <div class="stock ${isOutOfStock ? 'low-stock' : 'in-stock'}">
                        ${isOutOfStock ? 'Out of Stock' : `Qty: ${p.StockQty}`}
                    </div>
                </div>
                <button type="button" class="btn-add-cart" onclick="addToCart(${p.ProductID})" ${isOutOfStock ? 'disabled' : ''}>
                    <i class="fa-solid fa-cart-plus"></i>
                </button>
            </div>
        `;
        catalogContainer.appendChild(card);
    });
}

function addToCart(productId) {
    const product = state.products.find(p => p.ProductID === productId);
    if (!product) return;

    const existing = state.cart.find(item => item.productId === productId);
    if (existing) {
        if (existing.quantity >= product.StockQty) {
            alert(`Cannot add more. Only ${product.StockQty} items in stock.`);
            return;
        }
        existing.quantity += 1;
        existing.total = existing.quantity * existing.price;
    } else {
        state.cart.push({
            productId: product.ProductID,
            name: product.Name,
            price: product.Price,
            quantity: 1,
            total: product.Price
        });
    }

    updateCartUI();
}
function updateCartQuantity(productId, newQty) {
    const product = state.products.find(p => p.ProductID === productId);
    const cartItem = state.cart.find(item => item.productId === productId);
    if (!product || !cartItem) return;

    if (newQty <= 0) {
        state.cart = state.cart.filter(item => item.productId !== productId);
    } else if (newQty > product.StockQty) {
        alert(`Cannot set quantity to ${newQty}. Only ${product.StockQty} available.`);
        cartItem.quantity = product.StockQty;
        cartItem.total = cartItem.quantity * cartItem.price;
    } else {
        cartItem.quantity = newQty;
        cartItem.total = cartItem.quantity * cartItem.price;
    }

    updateCartUI();
}
function removeCartItem(productId) {
    state.cart = state.cart.filter(item => item.productId !== productId);
    updateCartUI();
}
function clearCart() {
    state.cart = [];
    updateCartUI();
}
function updateCartUI() {
    const cartList = document.getElementById('cart-items-list');
    cartList.innerHTML = '';

    if (state.cart.length === 0) {
        cartList.innerHTML = `
            <div class="empty-cart-msg">
                <i class="fa-solid fa-cart-shopping"></i>
                <p>Cart is currently empty. Click the cart icon on catalog items.</p>
            </div>
        `;
        document.getElementById('cart-pkr-subtotal').innerText = '€ 0.00';
        document.getElementById('cart-pkr-total').innerText = '€ 0.00';
        document.getElementById('cart-converted-total').innerText = '';
        return;
    }

    let subtotal = 0;
    state.cart.forEach(item => {
        subtotal += item.total;
        const row = document.createElement('div');
        row.className = 'cart-item';
        row.innerHTML = `
            <div class="cart-item-details">
                <div class="cart-item-name">${escapeHTML(item.name)}</div>
                <div class="cart-item-price">€ ${item.price.toFixed(2)} each</div>
            </div>
            <div class="cart-item-qty-control">
                <button type="button" class="qty-btn" onclick="updateCartQuantity(${item.productId}, ${item.quantity - 1})">-</button>
                <span class="cart-item-qty-val">${item.quantity}</span>
                <button type="button" class="qty-btn" onclick="updateCartQuantity(${item.productId}, ${item.quantity + 1})">+</button>
            </div>
            <div class="cart-item-subtotal">€ ${item.total.toFixed(2)}</div>
            <button type="button" class="cart-item-remove" onclick="removeCartItem(${item.productId})">
                <i class="fa-solid fa-trash"></i>
            </button>
        `;
        cartList.appendChild(row);
    });

    document.getElementById('cart-pkr-subtotal').innerText = `€ ${subtotal.toFixed(2)}`;
    document.getElementById('cart-pkr-total').innerText = `€ ${subtotal.toFixed(2)}`;

    handleCurrencyChange();
}

async function lookupCustomerForCart() {
    const phoneInput = document.getElementById('cart-customer-phone-search').value.trim();
    if (!phoneInput) {
        alert('Please enter a phone number.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/customers?phone=${encodeURIComponent(phoneInput)}`);
        const customers = await response.json();

        const matched = customers.find(c => c.phoneNumber === phoneInput) || customers[0];

        if (matched) {
            state.linkedCustomer = matched;
            document.getElementById('linked-customer-name').innerText = matched.name;
            document.getElementById('linked-customer-points').innerText = matched.loyaltyPoints;
            document.getElementById('linked-customer-banner').classList.remove('hidden');
            document.getElementById('register-quick-customer').classList.add('hidden');
        } else {

            state.linkedCustomer = null;
            document.getElementById('linked-customer-banner').classList.add('hidden');
            document.getElementById('register-quick-customer').classList.remove('hidden');
            document.getElementById('quick-cust-name').focus();
        }
    } catch (error) {
        console.error('Error looking up customer:', error);
    }
}
function unlinkCustomerFromCart() {
    state.linkedCustomer = null;
    document.getElementById('linked-customer-banner').classList.add('hidden');
    document.getElementById('cart-customer-phone-search').value = '';
}
async function quickRegisterCustomer() {
    const name = document.getElementById('quick-cust-name').value.trim();
    const phoneNumber = document.getElementById('cart-customer-phone-search').value.trim();

    if (!name || !phoneNumber) {
        alert('Please enter both name and phone number.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/customers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phoneNumber, loyaltyPoints: 0 })
        });

        const data = await response.json();
        if (response.ok) {
            state.linkedCustomer = {
                id: data.customerId,
                name: name,
                phoneNumber: phoneNumber,
                loyaltyPoints: 0
            };

            document.getElementById('linked-customer-name').innerText = name;
            document.getElementById('linked-customer-points').innerText = 0;
            document.getElementById('linked-customer-banner').classList.remove('hidden');
            document.getElementById('register-quick-customer').classList.add('hidden');
            document.getElementById('quick-cust-name').value = '';
        } else {
            alert(data.message || 'Error registering customer.');
        }
    } catch (error) {
        alert('Connection error.');
    }
}

function handleCurrencyChange() {
    const currency = document.getElementById('currency-convert-selector').value;
    state.selectedCurrency = currency;

    const subtotalText = document.getElementById('cart-pkr-total').innerText;
    const amountEur = parseFloat(subtotalText.replace('€ ', '')) || 0;

    const display = document.getElementById('cart-converted-total');

    if (currency === 'EUR' || amountEur === 0) {
        display.innerText = '';
        return;
    }

    const rate = state.exchangeRates[currency] || 1;
    const converted = amountEur * rate;

    const currencySymbols = {
        USD: '$',
        EUR: '€',
        GBP: '£',
        SAR: 'SR',
        AED: 'AED ',
        PKR: 'RS. '
    };
    const symbol = currencySymbols[currency] || '';

    display.innerText = `~ ${currency} ${symbol}${converted.toFixed(2)}`;
}

async function handleCheckout() {
    if (state.cart.length === 0) {
        alert('Cart is empty.');
        return;
    }

    const checkoutData = {
        userId: state.user.userId,
        customerId: state.linkedCustomer ? state.linkedCustomer.id : null,
        cartItems: state.cart.map(item => ({
            productId: item.productId,
            quantity: item.quantity
        }))
    };

    try {
        const response = await fetch(`${API_BASE_URL}/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(checkoutData)
        });

        const data = await response.json();
        if (response.ok && data.success) {
            alert('Bill generated and saved to the database successfully!');

            loadReceipt(data.orderId);

            loadEmployeeView();
        } else {
            alert(data.message || 'Error during checkout.');
        }
    } catch (error) {
        alert('Server transaction failure.');
    }
}

async function loadReceipt(invoiceId) {
    try {
        const response = await fetch(`${API_BASE_URL}/sales/invoice/${invoiceId}`);
        if (!response.ok) {
            alert('Invoice details could not be retrieved.');
            return;
        }

        const data = await response.json();
        renderReceiptModal(data);
    } catch (error) {
        console.error('Error loading receipt:', error);
    }
}
function renderReceiptModal(data) {
    const inv = data.invoice;
    const items = data.items;

    document.getElementById('rec-invoice-id').innerText = `#${inv.invoiceId}`;
    document.getElementById('rec-date').innerText = inv.date;
    document.getElementById('rec-cashier').innerText = inv.cashierName;
    document.getElementById('rec-cashier-id').innerText = inv.cashierId;

    const custRow = document.getElementById('rec-customer-row');
    if (inv.customerName) {
        document.getElementById('rec-customer-name').innerText = inv.customerName;
        document.getElementById('rec-customer-phone').innerText = inv.customerPhone;
        custRow.classList.remove('hidden');
    } else {
        custRow.classList.add('hidden');
    }

    const tbody = document.getElementById('rec-items-tbody');
    tbody.innerHTML = '';
    items.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${escapeHTML(item.name)}</td>
            <td class="text-center">${item.quantity}</td>
            <td class="text-right">€ ${item.unitPrice.toFixed(2)}</td>
            <td class="text-right">€ ${item.subtotal.toFixed(2)}</td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('rec-subtotal').innerText = `€ ${inv.totalAmount.toFixed(2)}`;
    document.getElementById('rec-grand-total').innerText = `€ ${inv.totalAmount.toFixed(2)}`;

    const convertedContainer = document.getElementById('rec-converted-rates-container');
    const currency = state.selectedCurrency;

    if (currency && currency !== 'EUR') {

        const rate = state.exchangeRates[currency] || 0;
        const converted = inv.totalAmount * rate;

        const symbols = { USD: '$', EUR: '€', GBP: '£', SAR: 'SR', AED: 'AED ', PKR: 'RS. ' };
        document.getElementById('rec-converted-total').innerText = `${currency} ${symbols[currency] || ''}${converted.toFixed(2)}`;
        convertedContainer.classList.remove('hidden');
    } else {
        convertedContainer.classList.add('hidden');
    }

    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://giftpoint.com/verify-invoice/${inv.invoiceId}`;
    document.getElementById('receipt-qr').src = qrUrl;

    document.getElementById('receipt-modal').classList.add('active');
}
function closeReceiptModal() {
    document.getElementById('receipt-modal').classList.remove('active');
}

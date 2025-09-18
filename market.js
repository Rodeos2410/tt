let products = [];

async function loadProducts() {
    try {
        const res = await fetch('http://localhost:8000/products');
        if (res.ok) {
            products = await res.json();
            return;
        }
        throw new Error('API returned ' + res.status);
    } catch (e) {
        // fallback to local samples
        products = [
            { id: 1, title: 'телеграм премиум', price: 299, img: '' },
            { id: 2, title: 'подписка open ai', price: 349, img: '' },
            { id: 3, title: 'подписка на Gemeni', price: 89, img: '' },
            { id: 4, title: '', price: 499, img: '' },
        ];
    }
}

const cart = JSON.parse(localStorage.getItem('cart') || '[]');

function formatPrice(v) {
    return v.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function renderProducts() {
    const root = document.getElementById('products');
    root.innerHTML = '';
    products.forEach(p => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <img src="${p.file_url || p.img}" alt="${p.title}">
            <div class="title">${p.title}</div>
            <div class="price">${formatPrice(p.price)} ₽</div>
            <div class="product-actions">
                <button class="button buy-btn" data-id="${p.id}">Купить</button>
                <button class="button add-btn" data-id="${p.id}">В корзину</button>
            </div>
        `;
        root.appendChild(card);
    });
    // re-attach event listener after rendering
    root.onclick = function(e) {
        const addBtn = e.target.closest('.add-btn');
        const buyBtn = e.target.closest('.buy-btn');
        if (addBtn) {
            const id = parseInt(addBtn.getAttribute('data-id'), 10);
            if (!isNaN(id)) addToCart(id);
            return;
        }
        if (buyBtn) {
            const id = parseInt(buyBtn.getAttribute('data-id'), 10);
            if (!isNaN(id)) {
                payForProduct(id);
            }
            return;
        }
    };
}

function addToCart(id) {
    const p = products.find(x => x.id === id);
    if (!p) return;
    const existing = cart.find(x => x.id === id);
    if (existing) existing.qty += 1;
    else cart.push({ ...p, qty: 1 });
    renderCart();
    saveCart();
}

function removeFromCart(id) {
    const idx = cart.findIndex(x => x.id === id);
    if (idx >= 0) cart.splice(idx, 1);
    renderCart();
    saveCart();
}

function renderCart() {
    const el = document.getElementById('cartItems');
    const totalEl = document.getElementById('cartTotal');
    const countEl = document.getElementById('cartCount');
    // Always update the small cart count (present in header) even if full cart panel is absent
    if (countEl) countEl.textContent = cart.reduce((s,i) => s + (i.qty||0), 0);
    if (!el) return; // don't render full cart if not on cart page
    el.innerHTML = '';
    let total = 0;
    if (cart.length === 0) {
        el.innerHTML = '';
    } else {
        cart.forEach(item => {
            const row = document.createElement('div');
            row.className = 'cart-item';
            row.innerHTML = `
                <div class="cart-left">
                    <div>${item.title} x${item.qty}</div>
                    <div class="cart-price">${formatPrice(item.price * item.qty)} ₽</div>
                </div>
                <div>
                    <button class="button" onclick="removeFromCart(${item.id})">Удалить</button>
                </div>
            `;
            el.appendChild(row);
            total += item.price * item.qty;
        });
    }
    if (totalEl) totalEl.textContent = formatPrice(total);
    if (countEl) countEl.textContent = cart.reduce((s,i) => s + i.qty, 0);
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
    // inform other tabs/windows
    try { localStorage.setItem('cart_update_ts', Date.now().toString()); } catch(e){}
}

function checkout() {
    if (cart.length === 0) {
        alert('Корзина пуста');
        return;
    }
    // if user is logged-in, post purchases to server
    const token = localStorage.getItem('authToken');
    if (token) {
        const items = cart.map(i => ({ product_id: i.id, qty: i.qty }));
        fetch('http://localhost:8000/purchase/bulk', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token }, body: JSON.stringify(items) })
            .then(async r => {
                if (!r.ok) {
                    const err = await r.json().catch(()=>({detail:'Ошибка сервера'}));
                    alert(err.detail || 'Ошибка сервера');
                    throw new Error('Ошибка сервера');
                }
                return r.json();
            }).then((data) => {
                alert('Заказ оформлен. Спасибо!\nОстаток баланса: ' + formatPrice(data.balance) + ' ₽');
                cart.length = 0;
                renderCart();
                saveCart();
            }).catch(() => {
                // error already shown
            });
        return;
    }
    // guest flow: just clear local cart
    alert('Заказ оформлен. Сумма: ' + formatPrice(cart.reduce((s, i) => s + i.price * i.qty, 0)) + ' ₽');
    cart.length = 0;
    renderCart();
}

// global for buttons in HTML
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.checkout = checkout;
function toggleCart() {
    const panel = document.getElementById('cartPanel');
    if (!panel) return;
    panel.classList.toggle('cart-panel--hidden');
    panel.classList.toggle('cart-panel--floating');
}
window.toggleCart = toggleCart;

document.addEventListener('DOMContentLoaded', () => {
    // load products from backend when available, otherwise use fallback
    // функция для оплаты одного товара сразу
    window.payForProduct = function(id) {
        const p = products.find(x => x.id === id);
        if (!p) return alert('Товар не найден');
        const token = localStorage.getItem('authToken');
        if (!token) {
            alert('Для оплаты войдите в аккаунт!');
            location.href = 'login.html';
            return;
        }
        fetch('http://localhost:8000/purchase/bulk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
            body: JSON.stringify([{ product_id: p.id, qty: 1 }])
        })
        .then(async r => {
            if (!r.ok) {
                const err = await r.json().catch(()=>({detail:'Ошибка сервера'}));
                alert(err.detail || 'Ошибка сервера');
                throw new Error('Ошибка сервера');
            }
            return r.json();
        })
        .then((data) => {
            alert('Покупка оформлена!\nОстаток баланса: ' + formatPrice(data.balance) + ' ₽');
        })
        .catch(() => {});
    }
    loadProducts().then(() => {
        renderProducts();
        renderCart();
    });
    // render cart counts only if the count element exists
    renderCart();
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) checkoutBtn.addEventListener('click', checkout);
    const toggleBtn = document.getElementById('cartToggle');
    if (toggleBtn) {
        // open the full cart page in the same tab for better UX
        toggleBtn.addEventListener('click', (e) => {
            // allow default navigation to cart.html
            // do not attempt to toggle inline panel because it's removed on main page
        });
    }
    // функция для оплаты одного товара сразу
    window.payForProduct = function(id) {
        const p = products.find(x => x.id === id);
        if (!p) return alert('Товар не найден');
        const token = localStorage.getItem('authToken');
        if (!token) {
            alert('Для оплаты войдите в аккаунт!');
            location.href = 'login.html';
            return;
        }
        fetch('http://localhost:8000/purchase/bulk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
            body: JSON.stringify([{ product_id: p.id, qty: 1 }])
        })
        .then(async r => {
            if (!r.ok) {
                const err = await r.json().catch(()=>({detail:'Ошибка сервера'}));
                alert(err.detail || 'Ошибка сервера');
                throw new Error('Ошибка сервера');
            }
            return r.json();
        })
        .then((data) => {
            alert('Покупка оформлена!\nОстаток баланса: ' + formatPrice(data.balance) + ' ₽');
        })
        .catch(() => {});
    }

    // listen for storage changes from other tabs/windows
    window.addEventListener('storage', (ev) => {
        if (ev.key === 'cart' || ev.key === 'cart_update_ts') {
            // reload cart from storage and re-render
            const remote = JSON.parse(localStorage.getItem('cart') || '[]');
            cart.length = 0;
            remote.forEach(i => cart.push(i));
            renderCart();
        }
    });

    // listen for messages (from cart.html)
    window.addEventListener('message', (ev) => {
        try {
            const data = ev.data || {};
            if (data.type === 'cartCleared') {
                cart.length = 0;
                saveCart();
                renderCart();
            }
        } catch(e){}
    });
});
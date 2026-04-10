const API = "";
const tokenKey = "catering_token";
const cartKey = "catering_cart";

const getToken = () => localStorage.getItem(tokenKey);
const setToken = (token) => localStorage.setItem(tokenKey, token);
const getCart = () => JSON.parse(localStorage.getItem(cartKey) || "[]");
const setCart = (cart) => localStorage.setItem(cartKey, JSON.stringify(cart));

async function api(path, options = {}) {
  const headers = options.headers || {};
  if (getToken()) headers.Authorization = `Bearer ${getToken()}`;
  if (!(options.body instanceof FormData)) headers["Content-Type"] = "application/json";
  const res = await fetch(`${API}${path}`, { ...options, headers });
  if (!res.ok) throw new Error((await res.json()).detail || "Request failed");
  return res.json();
}

async function loadMenu() {
  const list = document.getElementById("menuList");
  if (!list) return;
  const search = document.getElementById("searchInput")?.value || "";
  const category = document.getElementById("categoryFilter")?.value || "";
  const query = new URLSearchParams();
  if (search) query.append("search", search);
  if (category) query.append("category", category);
  const items = await api(`/menu?${query.toString()}`);
  list.innerHTML = items.map(i => `
    <div class="col-md-4">
      <div class="card menu-card"><div class="card-body">
        <h5>${i.name}</h5><div class="text-muted">${i.category}</div>
        <p>${i.description || ""}</p><strong>$${i.price.toFixed(2)}</strong>
        <button class="btn btn-sm btn-primary float-end" onclick="addToCart(${i.id}, '${i.name}', ${i.price})">Add</button>
      </div></div>
    </div>`).join("");
}

function addToCart(id, name, price) {
  const cart = getCart();
  const item = cart.find(x => x.menu_id === id);
  if (item) item.quantity += 1;
  else cart.push({ menu_id: id, name, price, quantity: 1 });
  setCart(cart);
  alert("Added to cart");
}

function loadCart() {
  const wrap = document.getElementById("cartItems");
  if (!wrap) return;
  const cart = getCart();
  let total = 0;
  wrap.innerHTML = cart.map((item, idx) => {
    const line = item.price * item.quantity;
    total += line;
    return `<div class='d-flex justify-content-between border p-2 mb-2'>
      <span>${item.name} x ${item.quantity}</span>
      <span>$${line.toFixed(2)} <button class='btn btn-sm btn-danger ms-2' onclick='removeCart(${idx})'>x</button></span>
    </div>`;
  }).join("") || "<p>No items in cart.</p>";
  document.getElementById("cartTotal").innerText = total.toFixed(2);
}

function removeCart(index) {
  const cart = getCart();
  cart.splice(index, 1);
  setCart(cart);
  loadCart();
}

async function bindAuth() {
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const msg = document.getElementById("authMessage");

  loginForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const data = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: document.getElementById("loginEmail").value,
          password: document.getElementById("loginPassword").value,
        })
      });
      setToken(data.access_token);
      msg.innerHTML = `<div class='alert alert-success'>Login successful.</div>`;
    } catch (err) {
      msg.innerHTML = `<div class='alert alert-danger'>${err.message}</div>`;
    }
  });

  registerForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          name: document.getElementById("regName").value,
          email: document.getElementById("regEmail").value,
          password: document.getElementById("regPassword").value,
        })
      });
      msg.innerHTML = `<div class='alert alert-success'>Registration successful. Please login.</div>`;
    } catch (err) {
      msg.innerHTML = `<div class='alert alert-danger'>${err.message}</div>`;
    }
  });
}

async function bindCheckout() {
  const form = document.getElementById("checkoutForm");
  if (!form) return;
  const msg = document.getElementById("checkoutMessage");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const cart = getCart();
    if (!cart.length) {
      msg.innerHTML = `<div class='alert alert-warning'>Cart is empty.</div>`;
      return;
    }

    try {
      const payload = {
        event_type: document.getElementById("eventType").value,
        guests: parseInt(document.getElementById("guests").value, 10),
        event_date: new Date(document.getElementById("eventDate").value).toISOString(),
        items: cart.map(c => ({ menu_id: c.menu_id, quantity: c.quantity })),
      };
      const order = await api("/orders", { method: "POST", body: JSON.stringify(payload) });
      setCart([]);
      msg.innerHTML = `<div class='alert alert-success'>Order #${order.id} placed. Total: $${order.total_price.toFixed(2)}</div>`;
    } catch (err) {
      msg.innerHTML = `<div class='alert alert-danger'>${err.message}</div>`;
    }
  });
}

async function bindAdmin() {
  const menuForm = document.getElementById("menuForm");
  if (!menuForm) return;

  try {
    const analytics = await api("/users/analytics/summary");
    document.getElementById("totalOrders").innerText = analytics.total_orders;
    document.getElementById("totalRevenue").innerText = `$${analytics.total_revenue.toFixed(2)}`;
    document.getElementById("totalCustomers").innerText = analytics.total_customers;

    const orders = await api("/orders");
    document.getElementById("adminOrders").innerHTML = orders.map(o => `
      <div class='border p-2 mb-2'>
        <div><strong>#${o.id}</strong> - ${o.customer_name} - $${o.total_price.toFixed(2)} - ${o.status}</div>
        <select onchange='updateOrderStatus(${o.id}, this.value)' class='form-select form-select-sm mt-2'>
          ${["Pending","Confirmed","Completed"].map(s=>`<option ${o.status===s?"selected":""}>${s}</option>`).join("")}
        </select>
      </div>`).join("");
  } catch (e) {
    document.getElementById("adminOrders").innerHTML = `<div class='alert alert-warning'>Admin token required.</div>`;
  }

  menuForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      name: document.getElementById("mName").value,
      category: document.getElementById("mCategory").value,
      price: parseFloat(document.getElementById("mPrice").value),
      description: document.getElementById("mDescription").value,
    };
    try {
      await api("/menu", { method: "POST", body: JSON.stringify(payload) });
      alert("Menu item added");
      menuForm.reset();
    } catch (err) {
      alert(err.message);
    }
  });
}

async function updateOrderStatus(id, status) {
  try {
    await api(`/orders/${id}`, { method: "PUT", body: JSON.stringify({ status }) });
  } catch (err) {
    alert(err.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadMenu().catch(() => {});
  loadCart();
  bindAuth();
  bindCheckout();
  bindAdmin();
});

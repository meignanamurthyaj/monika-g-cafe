document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("sidebar-container");
    if (!container) return;

    // Route guard: Check if user is logged in
    const token = localStorage.getItem("access_token");
    if (!token && !window.location.pathname.endsWith("login.html") && !window.location.pathname.endsWith("register.html")) {
        window.location.href = "login.html";
        return;
    }

    // Render sidebar HTML
    container.innerHTML = `
        <div class="sidebar-brand">
            <span class="brand-logo">☕</span>
            <span class="brand-text">Monika G Cafe</span>
        </div>
        <ul class="sidebar-menu">
            <li><a href="dashboard.html" id="nav-dashboard">📊 Dashboard</a></li>
            <li><a href="menu.html" id="nav-menu">🍟 Menu Catalog</a></li>
            <li><a href="orders.html" id="nav-orders">🛒 Order Desk</a></li>
            <li><a href="billing.html" id="nav-billing">🧾 Billing / Invoice</a></li>
            <li><a href="inventory.html" id="nav-inventory">📦 Inventory</a></li>
            <li><a href="employees.html" id="nav-employees">👥 Employees</a></li>
            <li><a href="customer.html" id="nav-customer">👤 Customers</a></li>
            <li><a href="reservation.html" id="nav-reservation">📅 Reservations</a></li>
            <li><a href="feedback.html" id="nav-feedback">💬 Feedback</a></li>
            <li><a href="report.html" id="nav-report">📈 Sales Reports</a></li>
        </ul>
        <div class="sidebar-footer">
            <button id="logoutBtn" class="btn btn-logout">🚪 Logout</button>
        </div>
    `;

    // Highlight active link based on current path
    const currentPath = window.location.pathname.split("/").pop();
    const navLinks = container.querySelectorAll(".sidebar-menu a");
    navLinks.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });

    // Logout listener
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("access_token");
            window.location.href = "login.html";
        });
    }
});

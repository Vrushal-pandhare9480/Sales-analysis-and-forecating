alert("Script Loaded");
const menuItems = document.querySelectorAll(".sidebar li");
const pages = document.querySelectorAll(".page");

menuItems.forEach(item => {

    item.addEventListener("click", () => {

        menuItems.forEach(li => li.classList.remove("active"));

        item.classList.add("active");

        pages.forEach(page => {

            page.style.display = "none";

        });

        const pageId = item.dataset.page;

        document.getElementById(pageId).style.display = "block";

        // Sales Data page open झाल्यावर data load करा
        if (pageId === "sales-data-page") {
            loadSalesTable();
}
    });

});

// ================= Dashboard Live Data =================

async function loadDashboardData() {

    try {

        const response = await fetch("https://sales-analysis-and-forecating.onrender.com/dashboard/summary");
        console.log(response);

        const data = await response.json();
        console.log(data);

        document.getElementById("total-sales").innerHTML =
            "₹" + (data.total_sales / 1000000).toFixed(2) + "M";

        document.getElementById("total-profit").innerHTML =
            "₹" + (data.total_profit / 1000).toFixed(0) + "K";

        document.getElementById("total-orders").innerHTML =
            data.total_orders;

    }

    catch(error){

        console.log("API Error :", error);

    }

}

loadDashboardData();
// ================= CATEGORY CHART =================

// ================= REGION CHART =================

async function loadDashboardRegionChart() {

    const response = await fetch("https://sales-analysis-and-forecating.onrender.com/analysis/region");

    const data = await response.json();

    const labels = data.map(item => item.region);

    const sales = data.map(item => item.sales);

    new Chart(document.getElementById("analysisregionChart"), {

        type: "pie",

        data: {

            labels: labels,

            datasets: [{

                data: sales

            }]

        },

        options: {

    responsive: true,

    plugins: {

        legend: {

            position: "right",

            labels: {

                font: {

                    size: 16

                }

            }

        }

    }

}

    });

}

loadDashboardRegionChart();

// ================= MONTHLY SALES TREND =================

async function loadMonthlySalesChart() {

    const response = await fetch("https://sales-analysis-and-forecating.onrender.com/analysis/monthly-sales");

    const data = await response.json();

    const labels = data.map(item => item.month);

    const sales = data.map(item => item.sales);

    new Chart(document.getElementById("monthlySalesChart"), {

        type: "line",

        data: {

            labels: labels,

            datasets: [{

                label: "Monthly Sales",

                data: sales,

                borderWidth: 3,

                tension: 0.4,

                fill: false

            }]

        },

        options: {

    responsive: true,

    plugins: {

        legend: {

            display: false

        }

    },

    scales: {

        x: {

            ticks: {

                color: "#ffffff",

                font: {

                    size: 16,

                    weight: "bold"

                }

            }

        },

        y: {

            beginAtZero: true,

            ticks: {

                color: "#ffffff",

                font: {

                    size: 16,

                    weight: "bold"

                }

            }

        }

    }

}

    });

}

loadMonthlySalesChart();

let forecastPageChart = null;

async function loadForecastChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/forecast-data"
        );

        const forecastData = await response.json();

        const response2 = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/monthly-sales"
        );

        const monthlyData = await response2.json();

        const labels = [];
        const actualSales = [];
        const predictedSales = [];

        monthlyData.forEach(item => {

            labels.push(item.month);

            actualSales.push(
                Number(item.sales)
            );

            predictedSales.push(null);

        });

        forecastData.forEach(item => {

            labels.push(item.Month);

            actualSales.push(null);

            predictedSales.push(
                Number(item.Predicted_Sales)
            );

        });

        const canvas =
            document.getElementById("forecastChart");

        if (!canvas) {
            console.log("forecastChart NOT FOUND");
            return;
        }

        if (forecastPageChart) {
            forecastPageChart.destroy();
        }

        forecastPageChart = new Chart(canvas, {

            type: "line",

            data: {

                labels: labels,

                datasets: [

                    {
                        label: "Actual Sales",

                        data: actualSales,

                        borderColor: "#ec4899",

                        backgroundColor: "transparent",

                        borderWidth: 3,

                        pointRadius: 3,

                        tension: 0.4
                    },

                    {
                        label: "Forecast",

                        data: predictedSales,

                        borderColor: "#06b6d4",

                        backgroundColor: "transparent",

                        borderWidth: 3,

                        borderDash: [7, 5],

                        pointRadius: 4,

                        tension: 0.4
                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        position: "top",

                        labels: {
                            color: "#ffffff"
                        }

                    }

                },

                scales: {

                    x: {

                        ticks: {
                            color: "#94a3b8"
                        },

                        grid: {
                            display: false
                        }

                    },

                    y: {

                        beginAtZero: true,

                        ticks: {

                            color: "#94a3b8",

                            callback: function(value) {
                                return "₹" +
                                    (value / 1000) +
                                    "K";
                            }

                        },

                        grid: {
                            color:
                                "rgba(255,255,255,0.08)"
                        }

                    }

                }

            }

        });

    }

    catch (error) {

        console.log(
            "Forecast Chart Error:",
            error
        );

    }

}

loadForecastChart();


async function loadTopProductsChart() {

    try {

        const response = await fetch("https://sales-analysis-and-forecating.onrender.com/analysis/top-products");

        const data = await response.json();

        const labels = data.map(item => item["Product Name"]);
        const sales = data.map(item => item.Sales);

        const ctx = document.getElementById("topProductsChart");

        new Chart(ctx, {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{

                    label: "Sales",

                    data: sales,

                    backgroundColor: "#3b82f6",

                    borderRadius: 8

                }]

            },

            options: {

                indexAxis: "y",

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        labels: {

                            color: "#ffffff"

                        }

                    }

                },

                scales: {

                    x: {

                        ticks: {

                            color: "#ffffff"

                        },

                        grid: {

                            color: "rgba(255,255,255,0.1)"

                        }

                    },

                    y: {

                        ticks: {

                            color: "#ffffff"

                        },

                        grid: {

                            display: false

                        }

                    }

                }

            }

        });

    }

    catch(error){

        console.log("Top Products Error:", error);

    }

}

loadTopProductsChart();

// ================= Reports =================

document.getElementById("downloadSalesCSV").addEventListener("click", () => {

    window.open(
        "https://sales-analysis-and-forecating.onrender.com/reports/sales-csv",
        "_blank"
    );

});

const pdfBtn = document.getElementById("downloadPDF");

if(pdfBtn){

    pdfBtn.addEventListener("click",()=>{

        window.open(
            "https://sales-analysis-and-forecating.onrender.com/reports/dashboard-pdf",
            "_blank"
        );

    });

}

const forecastBtn = document.getElementById("downloadForecastCSV");

if (forecastBtn) {

    forecastBtn.addEventListener("click", () => {

        window.open(
            "https://sales-analysis-and-forecating.onrender.com/reports/forecast-csv",
            "_blank"
        );

    });

}

async function loadSalesTable() {

    const salesPage = document.getElementById("sales-data-page");

    salesPage.style.display = "block";
    salesPage.style.visibility = "visible";
    salesPage.style.opacity = "1";

    // बाकीचा code...
    try {

        const response = await fetch("https://sales-analysis-and-forecating.onrender.com/analysis/sales-data");

        const data = await response.json();

        console.log(data);

        const tbody = document.getElementById("salesTableBody");

        console.log(tbody); 
        
        tbody.innerHTML = "";

        data.forEach(item => {

            tbody.innerHTML += `
                <tr>
                    <td>${item["Order ID"]}</td>
                    <td>${item["Product Name"]}</td>
                    <td>${item.Category}</td>
                    <td>${item.Region}</td>
                    <td>₹${Number(item.Sales).toFixed(2)}</td>
                    <td>₹${Number(item.Profit).toFixed(2)}</td>
                </tr>
            `;
            
        });
        console.log("Rows in table:", tbody.querySelectorAll("tr").length);
        tbody.closest(".table-card").style.display = "block";
        tbody.closest(".table-card").style.visibility = "visible";
        tbody.closest(".table-card").style.opacity = "1";
    }

    catch(error){

        console.log("Sales Table Error:", error);

    }

console.log(document.getElementById("salesTableBody"));
console.log("Rows in table:", tbody.querySelectorAll("tr").length);

tbody.style.visibility = "visible";

}


// ======================================================
// CUSTOMER REGION CHART
// ======================================================

let customerRegionChart = null;

// ======================================================
// CUSTOMER REGION CHART
// ======================================================

let customersRegionChartInstance = null;



// ======================================================
// CUSTOMER GROWTH CHART
// ======================================================

let customerGrowthChartInstance = null;

async function loadCustomerGrowthChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/customer-growth"
        );

        if (!response.ok) {
            throw new Error(
                `HTTP Error: ${response.status}`
            );
        }

        const data = await response.json();

        console.log(
            "Customer Growth:",
            data
        );

        const canvas =
            document.getElementById("customerGrowthChart");

        if (!canvas) {
            console.log(
                "customerGrowthChart canvas not found"
            );
            return;
        }

        // Existing chart destroy
        if (customerGrowthChartInstance) {
            customerGrowthChartInstance.destroy();
        }

        const labels = data.map(
            item =>
                item.Month ??
                item.month
        );

        const customers = data.map(
            item => Number(
                item.Customers ??
                item.customers ??
                item.total_customers
            )
        );

        customerGrowthChartInstance =
            new Chart(canvas, {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [{

                        label: "Customers",

                        data: customers,

                        borderColor: "#3b82f6",

                        backgroundColor:
                            "rgba(59,130,246,0.12)",

                        borderWidth: 3,

                        pointBackgroundColor:
                            "#3b82f6",

                        pointBorderColor:
                            "#3b82f6",

                        pointRadius: 4,

                        pointHoverRadius: 6,

                        tension: 0.4,

                        fill: true

                    }]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {
                            display: false
                        }

                    },

                    scales: {

                        x: {

                            ticks: {
                                color: "#ffffff"
                            },

                            grid: {
                                display: false
                            }

                        },

                        y: {

                            beginAtZero: true,

                            ticks: {
                                color: "#ffffff"
                            },

                            grid: {
                                color:
                                    "rgba(255,255,255,0.08)"
                            }

                        }

                    }

                }

            });

    }
    catch (error) {

        console.error(
            "Customer Growth Chart Error:",
            error
        );

    }

}

loadCustomerGrowthChart()

// ======================================================
// LOAD CUSTOMER CHARTS
// ======================================================

async function loadCustomerCharts() {

    await Promise.all([

        loadCustomersRegionChart(),

        loadCustomerGrowthChart()

    ]);

}

// ======================================================
// START CUSTOMER CHARTS
// ======================================================


// ======================================================
// START
// ======================================================

// ======================================================
// CUSTOMER CHARTS
// ======================================================

// ======================================================
// CUSTOMER SUMMARY
// ======================================================

async function loadCustomerSummary() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/customer-summary"
        );

        const data = await response.json();

        document.getElementById("totalCustomers").innerText =
            data.TotalCustomers;

        document.getElementById("newCustomers").innerText =
            data.NewCustomers;

        document.getElementById("repeatCustomers").innerText =
            data.RepeatCustomers;

        document.getElementById("retentionRate").innerText =
            data.RetentionRate + "%";

    }
    catch (error) {

        console.error(
            "Customer Summary Error:",
            error
        );

    }

}


// ======================================================
// START CUSTOMER PAGE
// ======================================================

loadCustomerCharts();

loadCustomerSummary();



async function loadCustomersTable() {

    try {

        const limit = document.getElementById("customerLimit").value;
        const search = document.getElementById("customerSearch").value;
        const region = document.getElementById("customerRegion").value;
        const segment = document.getElementById("customerSegment").value;

        console.log("Limit =", limit);

        const response = await fetch(`https://sales-analysis-and-forecating.onrender.com/analysis/customers?limit=${limit}&search=${search}&region=${region}&segment=${segment}`);

        const data = await response.json();

        const tbody = document.getElementById("customersTableBody");

        tbody.innerHTML = "";

        data.forEach(item => {

            tbody.innerHTML += `
                <tr>
                    <td>${item["Customer Name"]}</td>
                    <td>${item.Segment}</td>
                    <td>${item.Region}</td>
                    <td>${item.Orders}</td>
                    <td>₹${Number(item.Sales).toFixed(2)}</td>
                    <td>₹${Number(item.Profit).toFixed(2)}</td>
                </tr>
            `;

        });

    }

    catch(error){

        console.log("Customers Table Error:", error);

    }

}

loadCustomersTable();

document
    .getElementById("loadCustomersBtn")
    .addEventListener("click", loadCustomersTable);

document
    .getElementById("customerSearch")
    .addEventListener("keyup", loadCustomersTable);

document
    .getElementById("customerRegion")
    .addEventListener("change", loadCustomersTable);

document
    .getElementById("customerSegment")
    .addEventListener("change", loadCustomersTable);

async function loadProductsTable() {

    try {

        const limit =
            document.getElementById("productLimit").value;

        const search =
            document.getElementById("productSearch").value;

        const category =
            document.getElementById("productCategory").value;

        const response = await fetch(
            `https://sales-analysis-and-forecating.onrender.com/analysis/products?limit=${limit}&search=${encodeURIComponent(search)}&category=${encodeURIComponent(category)}`
        );

        const data = await response.json();

        const tbody =
            document.getElementById("productsTableBody");

        tbody.innerHTML = "";

        data.forEach(item => {

            tbody.innerHTML += `
                <tr>

                    <td>${item["Product Name"]}</td>

                    <td>${item.Category}</td>

                    <td>₹${Number(item.Sales).toFixed(2)}</td>

                    <td class="${Number(item.Profit) >= 0 ? 'profit-positive' : 'profit-negative'}">
                        ₹${Number(item.Profit).toFixed(2)}
                    </td>

                    <td>${Number(item.Quantity).toFixed(0)}</td>

                </tr>
            `;

        });

    }

    catch(error) {

        console.log("Products Table Error:", error);

    }

}

loadProductsTable();

document
    .getElementById("loadProductsBtn")
    .addEventListener("click", loadProductsTable);

document
    .getElementById("productSearch")
    .addEventListener("keyup", loadProductsTable);

document
    .getElementById("productCategory")
    .addEventListener("change", loadProductsTable);

async function loadProductCategories() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/product-categories"
        );

        const data = await response.json();

        const select =
            document.getElementById("productCategory");

        // Existing "All Categories" ठेव
        select.innerHTML = `
            <option value="">All Categories</option>
        `;

        data.forEach(item => {

            select.innerHTML += `
                <option value="${item.Category}">
                    ${item.Category}
                </option>
            `;

        });

    }

    catch(error) {

        console.log("Product Categories Error:", error);

    }

}

loadProductCategories();

async function loadProductsChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/top-products"
        );

        const data = await response.json();

        const labels = data.map(
            item => item["Product Name"]
        );

        const sales = data.map(
            item => Number(item.Sales)
        );

        const ctx =
            document.getElementById("productsChart");

        new Chart(ctx, {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{

                    label: "Sales",

                    data: sales,

                    backgroundColor: "#3b82f6",

                    borderRadius: 8

                }]

            },

            options: {

    indexAxis: "y",

    responsive: true,

    maintainAspectRatio: false,

    plugins: {

        legend: {
            display: false
        }

    },

    scales: {

        x: {
            ticks: {
                color: "#ffffff"
            },

            grid: {
                color: "rgba(255,255,255,0.1)"
            }
        },

        y: {
            ticks: {
                color: "#ffffff",
                font: {
                    size: 11
                }
            },

            grid: {
                display: false
            }
        }

    }

}

        });

    }

    catch(error) {

        console.log(
            "Products Chart Error:",
            error
        );

    }

}

loadProductsChart();

let dashboardCategoryChart = null;

async function loadDashboardCategoryChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/category-sales"
        );

        const data = await response.json();

        const labels = data.map(
            item => item.Category
        );

        const sales = data.map(
            item => Number(item.Sales)
        );

        const canvas =
            document.getElementById("dashboardCategoryChart");

        if (!canvas) return;

        if (dashboardCategoryChart) {
            dashboardCategoryChart.destroy();
        }

        dashboardCategoryChart = new Chart(canvas, {

            type: "doughnut",

            data: {

                labels: labels,

                datasets: [{

                    data: sales,

                    backgroundColor: [
                        "#3b82f6",
                        "#10b981",
                        "#f59e0b"
                    ],

                    borderColor: "#1e293b",

                    borderWidth: 2

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        position: "bottom",

                        labels: {
                            color: "#ffffff",
                            padding: 18
                        }

                    }

                }

            }

        });

    } catch (error) {

        console.log(
            "Dashboard Category Chart Error:",
            error
        );

    }

}

async function loadProductsCategoryChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/category-sales"
        );

        const data = await response.json();

        const labels = data.map(
            item => item.Category
        );

        const sales = data.map(
            item => Number(item.Sales)
        );

        const ctx = document.getElementById(
            "productsCategoryChart"
        );

        if (!ctx) return;

        new Chart(ctx, {

            type: "doughnut",

            data: {

                labels: labels,

                datasets: [{

                    label: "Sales",

                    data: sales,

                    backgroundColor: [
                        "#3b82f6",
                        "#10b981",
                        "#f59e0b"
                    ],

                    borderWidth: 2

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        position: "bottom",

                        labels: {
                            color: "#ffffff"
                        }

                    }

                }

            }

        });

    }

    catch(error) {

        console.log(
            "Products Category Chart Error:",
            error
        );

    }

}

loadProductsCategoryChart();

async function loadProductSummary() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/product-summary"
        );

        const data = await response.json();

        document.getElementById("totalProducts").textContent =
            data.TotalProducts;

        document.getElementById("totalCategories").textContent =
            data.TotalCategories;

        document.getElementById("bestProduct").textContent =
            data.BestProduct;

        document.getElementById("avgSales").textContent =
            "₹" + Number(data.AvgSales).toFixed(2);
        
        const bestProduct =
        document.getElementById("bestProduct");

        bestProduct.textContent = data.BestProduct;
        bestProduct.title = data.BestProduct;

    }

    catch(error) {

        console.log(
            "Product Summary Error:",
            error
        );

    }

}

loadProductSummary();

async function loadRegionSalesChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/region-sales"
        );

        const data = await response.json();
        console.log("REGION SALES DATA:", data);

        const labels = data.map(
            item => item.Region
        );

        const sales = data.map(
            item => Number(item.Sales)
        );

        const canvas =
            document.getElementById("regionSalesChart");

        if (!canvas) return;

        new Chart(canvas, {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{

                    label: "Sales",

                    data: sales,

                    backgroundColor: "#3b82f6",

                    borderRadius: 8

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    x: {

                        ticks: {
                            color: "#ffffff"
                        },

                        grid: {
                            display: false
                        }

                    },

                    y: {

                        ticks: {
                            color: "#ffffff"
                        },

                        grid: {
                            color: "rgba(255,255,255,0.1)"
                        }

                    }

                }

            }

        });

    }

    catch(error) {

        console.log(
            "Region Sales Chart Error:",
            error
        );

    }

}

loadRegionSalesChart();

async function loadRegionPerformance() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/region-performance"
        );

        const data = await response.json();

        const tbody =
            document.getElementById("regionTableBody");

        if (!tbody) return;

        tbody.innerHTML = "";

        data.forEach(item => {

            tbody.innerHTML += `
                <tr>

                    <td>${item.Region}</td>

                    <td>₹${Number(item.Sales).toLocaleString("en-IN", {
                        maximumFractionDigits: 2
                    })}</td>

                    <td class="${
                        Number(item.Profit) >= 0
                            ? "profit-positive"
                            : "profit-negative"
                    }">
                        ₹${Number(item.Profit).toLocaleString("en-IN", {
                            maximumFractionDigits: 2
                        })}
                    </td>

                    <td>${Number(item.Orders).toLocaleString("en-IN")}</td>

                </tr>
            `;

        });

    }

    catch(error) {

        console.log(
            "Region Performance Error:",
            error
        );

    }

}

loadRegionPerformance();

async function loadRegionProfitChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/region-profit"
        );

        const data = await response.json();
        console.log("REGION PROFIT DATA:", data);

        const labels = data.map(
            item => item.Region
        );

        const profit = data.map(
            item => Number(item.Profit)
        );

        const canvas =
            document.getElementById("regionProfitChart");

        if (!canvas) return;

        new Chart(canvas, {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{

                    label: "Profit",

                    data: profit,

                    backgroundColor: "#22c55e",

                    borderRadius: 8

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    x: {

                        ticks: {
                            color: "#ffffff"
                        },

                        grid: {
                            display: false
                        }

                    },

                    y: {

                        ticks: {
                            color: "#ffffff"
                        },

                        grid: {
                            color: "rgba(255,255,255,0.1)"
                        }

                    }

                }

            }

        });

    }

    catch(error) {

        console.log(
            "Region Profit Chart Error:",
            error
        );

    }

}

loadRegionProfitChart();

async function loadRegionKPIs() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/region-kpis"
        );

        const data = await response.json();

        console.log("REGION KPI DATA:", data);

        document.getElementById("bestRegion").textContent =
            data.best_region;

        document.getElementById("totalRegions").textContent =
            data.total_regions;

        document.getElementById("highestRegionSales").textContent =
            "₹" + Number(data.highest_sales).toLocaleString("en-IN", {
                maximumFractionDigits: 2
            });

        document.getElementById("highestRegionProfit").textContent =
            "₹" + Number(data.highest_profit).toLocaleString("en-IN", {
                maximumFractionDigits: 2
            });

    }

    catch(error) {

        console.log(
            "Region KPI Error:",
            error
        );

    }

}

loadRegionKPIs();

let salesOffset = 0;

const firstLoad = 70;
const nextLoad = 100;


let allSalesData = [];

async function loadSalesData() {

    try {

        const limit =
        Number(document.getElementById("salesLimit").value) || 10;

        const response = await fetch(
            `https://sales-analysis-and-forecating.onrender.com/analysis/sales-data?limit=${limit}&offset=0`
        );

        if (!response.ok) {
            throw new Error(`Server Error: ${response.status}`);
        }

        allSalesData = await response.json();

        console.log("Sales Data:", allSalesData);

        renderSalesTable(allSalesData);

    } catch (error) {

        console.error(
            "Sales Data Error:",
            error
        );

    }
}
document.getElementById("salesLimit").addEventListener(
    "change",
    loadSalesData
);

function renderSalesTable(data) {

    const tbody =
        document.getElementById("salesTableBody");

    if (!tbody) {
        console.log("salesTableBody not found");
        return;
    }

    tbody.innerHTML = "";

    data.forEach(item => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>
                ${item["Order ID"] ?? "-"}
            </td>

            <td>
                ${item["Product Name"] ?? "-"}
            </td>

            <td>
                ${item["Category"] ?? "-"}
            </td>

            <td>
                ${item["Region"] ?? "-"}
            </td>

            <td>
                ₹${Number(item["Sales"] ?? 0).toLocaleString("en-IN", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })}
            </td>

            <td>
                ₹${Number(item["Profit"] ?? 0).toLocaleString("en-IN", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })}
            </td>
        `;

        tbody.appendChild(row);

    });

    console.log(
        "Rows displayed:",
        data.length
    );
}

const salesSearch =
    document.getElementById("salesSearch");

const salesCategory =
    document.getElementById("salesCategory");

const salesRegion =
    document.getElementById("salesRegion");


function applySalesFilters() {

    const searchValue =
        salesSearch.value.trim().toLowerCase();

    const categoryValue =
        salesCategory.value;

    const regionValue =
        salesRegion.value;


    const filteredData =
        allSalesData.filter(item => {

            const product =
                String(item["Product Name"] ?? "")
                    .toLowerCase();

            const category =
                String(item["Category"] ?? "");

            const region =
                String(item["Region"] ?? "");


            const matchesSearch =
                product.includes(searchValue);

            const matchesCategory =
                categoryValue === "" ||
                category === categoryValue;

            const matchesRegion =
                regionValue === "" ||
                region === regionValue;


            return (
                matchesSearch &&
                matchesCategory &&
                matchesRegion
            );
        });


    renderSalesTable(filteredData);
}

salesSearch.addEventListener(
    "input",
    applySalesFilters
);

salesCategory.addEventListener(
    "change",
    applySalesFilters
);

salesRegion.addEventListener(
    "change",
    applySalesFilters
);

loadSalesData();

async function loadSalesByCategoryChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/category-sales"
        );

        const data = await response.json();

        const labels = data.map(
            item => item.Category
        );

        const sales = data.map(
            item => Number(item.Sales)
        );

        const canvas =
            document.getElementById("analysisCategoryChart");

        if (!canvas) return;

        new Chart(canvas, {

            type: "doughnut",

            data: {

                labels: labels,

                datasets: [{

                    data: sales,

                    backgroundColor: [
                        "#3b82f6",
                        "#10b981",
                        "#f59e0b"
                    ],

                    borderWidth: 2

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        position: "bottom",

                        labels: {
                            color: "#ffffff"
                        }

                    }

                }

            }

        });

    }

    catch (error) {

        console.log(
            "Sales Category Chart Error:",
            error
        );

    }

}

async function loadSalesByRegionChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/region-sales"
        );

        const data = await response.json();

        const labels = data.map(
            item => item.Region
        );

        const sales = data.map(
            item => Number(item.Sales)
        );

        const canvas =
            document.getElementById("analysisRegionChart");

        if (!canvas) return;

        new Chart(canvas, {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{

                    label: "Sales",

                    data: sales,

                    backgroundColor: "#10b981",

                    borderRadius: 8

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    x: {
                        ticks: {
                            color: "#ffffff"
                        },

                        grid: {
                            display: false
                        }
                    },

                    y: {
                        ticks: {
                            color: "#ffffff"
                        },

                        grid: {
                            color:
                                "rgba(255,255,255,0.1)"
                        }
                    }

                }

            }

        });

    }

    catch (error) {

        console.log(
            "Sales Region Chart Error:",
            error
        );

    }

}

loadSalesByCategoryChart();
loadSalesByRegionChart();

async function loadDashboardKPI() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/dashboard-kpi"
        );

        const data = await response.json();

        console.log("Dashboard KPI:", data);

        document.getElementById("total-sales").textContent =
            "₹" + (data.total_sales / 1000000).toFixed(2) + "M";

        document.getElementById("total-profit").textContent =
            "₹" + (data.total_profit / 1000).toFixed(0) + "K";

        document.getElementById("total-orders").textContent =
            Number(data.total_orders).toLocaleString("en-IN");

        document.getElementById("total-customers").textContent =
            Number(data.total_customers).toLocaleString("en-IN");

    }

    catch (error) {

        console.log(
            "Dashboard KPI Error:",
            error
        );

    }
}

loadDashboardKPI();

async function loadAnalysisRegionChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/region-sales"
        );

        const data = await response.json();

        console.log("Region Sales:", data);

        const labels = data.map(
            item => item.Region
        );

        const sales = data.map(
            item => Number(item.Sales)
        );

        const ctx =
            document.getElementById("regionChart");

        if (!ctx) {
            console.log("regionChart canvas not found");
            return;
        }

        new Chart(ctx, {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{

                    label: "Sales",

                    data: sales,

                    backgroundColor: "#06b6d4",

                    borderRadius: 8

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        labels: {
                            color: "#ffffff"
                        }
                    }

                },

                scales: {

                    x: {

                        ticks: {
                            color: "#ffffff"
                        },

                        grid: {
                            display: false
                        }

                    },

                    y: {

                        beginAtZero: true,

                        ticks: {
                            color: "#ffffff"
                        }

                    }

                }

            }

        });

    }

    catch (error) {

        console.log(
            "Region Chart Error:",
            error
        );

    }

}

loadAnalysisRegionChart();

async function loadCategoryChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/category-sales"
        );

        const data = await response.json();

        console.log("CATEGORY API:", data);

        const labels = data.map(item => item.Category);

        const sales = data.map(item => Number(item.Sales));

        console.log("CATEGORY LABELS:", labels);
        console.log("CATEGORY SALES:", sales);

        const canvas =
            document.getElementById("dashboardCategoryChart");

        console.log("CATEGORY CANVAS:", canvas);

        if (!canvas) {
            console.log("dashboardCategoryChart NOT FOUND");
            return;
        }

        new Chart(canvas, {

            type: "doughnut",

            data: {

                labels: labels,

                datasets: [{

                    data: sales,

                    backgroundColor: [
                        "#3b82f6",
                        "#10b981",
                        "#f59e0b"
                    ],

                    borderColor: "#1e293b",

                    borderWidth: 2

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        position: "bottom",

                        labels: {
                            color: "#ffffff",
                            padding: 18
                        }

                    }

                }

            }

        });

    }

    catch (error) {

        console.log(
            "CATEGORY CHART ERROR:",
            error
        );

    }

}

loadCategoryChart();

let salesTrendChart = null;

async function loadSalesTrendChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/monthly-sales"
        );

        const data = await response.json();

        console.log("Monthly Sales:", data);

        const labels = data.map(
            item => item.month
        );

        const sales = data.map(
            item => Number(item.sales)
        );

        const canvas =
            document.getElementById("salesTrendChart");

        if (!canvas) {
            console.log("salesTrendChart NOT FOUND");
            return;
        }

        if (salesTrendChart) {
            salesTrendChart.destroy();
        }

        salesTrendChart = new Chart(canvas, {

            type: "line",

            data: {

                labels: labels,

                datasets: [{

                    label: "Sales",

                    data: sales,

                    borderColor: "#d946ef",

                    backgroundColor: "rgba(217,70,239,0.15)",

                    borderWidth: 3,

                    tension: 0.4,

                    fill: true,

                    pointRadius: 3

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        labels: {
                            color: "#ffffff"
                        }

                    }

                },

                scales: {

                    x: {

                        ticks: {
                            color: "#ffffff"
                        },

                        grid: {
                            display: false
                        }

                    },

                    y: {

                        beginAtZero: true,

                        ticks: {
                            color: "#ffffff"
                        },

                        grid: {
                            color: "rgba(255,255,255,0.08)"
                        }

                    }

                }

            }

        });

    }

    catch (error) {

        console.log(
            "Sales Trend Chart Error:",
            error
        );

    }

}

loadSalesTrendChart();

let dashboardForecastChart = null;

async function loadDashboardForecastChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/forecast-data"
        );

        const forecastData = await response.json();

        const response2 = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/monthly-sales"
        );

        const monthlyData = await response2.json();

        const labels = [];
        const actualSales = [];
        const predictedSales = [];

        // Actual Sales
        monthlyData.forEach(item => {

            labels.push(item.month);

            actualSales.push(
                Number(item.sales)
            );

            predictedSales.push(null);

        });

        // Predicted Sales
        forecastData.forEach(item => {

            labels.push(item.Month);

            actualSales.push(null);

            predictedSales.push(
                Number(item.Predicted_Sales)
            );

        });

        const canvas =
        document.getElementById("dashboardForecastChart");

        if (!canvas) {
            console.log("forecastChart NOT FOUND");
            return;
        }

        // Destroy old chart if already created
        if (dashboardForecastChart) {
            dashboardForecastChart.destroy();
        }

        dashboardForecastChart = new Chart(canvas, {

            type: "line",

            data: {

                labels: labels,

                datasets: [

                    {
                        label: "Actual Sales",

                        data: actualSales,

                        borderColor: "#3b82f6",

                        backgroundColor: "#3b82f6",

                        borderWidth: 3,

                        tension: 0.4
                    },

                    {
                        label: "Predicted Sales",

                        data: predictedSales,

                        borderColor: "#ef4444",

                        backgroundColor: "#ef4444",

                        borderWidth: 3,

                        borderDash: [8, 5],

                        tension: 0.4
                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        labels: {
                            color: "#ffffff"
                        }

                    }

                },

                scales: {

                    x: {

                        ticks: {
                            color: "#ffffff"
                        },

                        grid: {
                            display: false
                        }

                    },

                    y: {

                        beginAtZero: true,

                        ticks: {
                            color: "#ffffff"
                        }

                    }

                }

            }

        });

    }

    catch (error) {

        console.log(
            "Dashboard Forecast Chart Error:",
            error
        );

    }

}

loadDashboardForecastChart();

async function loadDashboardSummary() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/dashboard/summary"
        );

        if (!response.ok) {
            throw new Error("Failed to fetch dashboard summary");
        }

        const data = await response.json();

        console.log("DASHBOARD SUMMARY:", data);

        document.getElementById("total-sales").textContent =
            "₹" + Number(data.total_sales).toLocaleString("en-IN", {
                maximumFractionDigits: 2
            });

        document.getElementById("total-profit").textContent =
            "₹" + Number(data.total_profit).toLocaleString("en-IN", {
                maximumFractionDigits: 2
            });

        document.getElementById("total-orders").textContent =
            Number(data.total_orders).toLocaleString("en-IN");

    }

    catch (error) {

        console.error(
            "Dashboard Summary Error:",
            error
        );

    }

}

loadDashboardSummary();

// ===============================
// RECENT ORDERS
// ===============================


async function loadRecentOrders(limit = 10) {

    try {

        const response = await fetch(
            `https://sales-analysis-and-forecating.onrender.com/analysis/sales-data?limit=${limit}&offset=0`
        );

        if (!response.ok) {
            throw new Error(`Server Error: ${response.status}`);
        }

        const data = await response.json();

        const tbody =
            document.getElementById("recentOrdersTableBody");

        if (!tbody) {
            console.error("recentOrdersTableBody NOT FOUND");
            return;
        }

        tbody.innerHTML = "";

        data.forEach(order => {

            const row = document.createElement("tr");

            const orderId =
                order["Order ID"] ??
                order.Order_ID ??
                "-";

            const product =
                order["Product Name"] ??
                order.Product_Name ??
                "-";

            const region =
                order["Region"] ??
                "-";

            const sales =
                Number(order["Sales"] ?? 0);

            const profit =
                Number(order["Profit"] ?? 0);

            row.innerHTML = `
                <td>${orderId}</td>
                <td>${product}</td>
                <td>${region}</td>
                <td>
                    ₹${sales.toLocaleString("en-IN", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    })}
                </td>
                <td>
                    ₹${profit.toLocaleString("en-IN", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    })}
                </td>
            `;

            tbody.appendChild(row);

        });

    } catch (error) {

        console.error("Recent Orders Error:", error);

    }
}


// ===============================
// LIMIT FILTER
// ===============================

const recentOrdersLimit =
    document.getElementById("recentOrdersLimit");

if (recentOrdersLimit) {

    recentOrdersLimit.addEventListener(
        "change",
        function () {

            let limit = Number(this.value);

            if (limit < 1) {
                limit = 1;
                this.value = 1;
            }

            loadRecentOrders(limit);

        }
    );

}


// Initial load
loadRecentOrders(10);

async function loadForecastKPIs() {

    const accuracyResponse = await fetch(
    "https://sales-analysis-and-forecating.onrender.com/analysis/forecast-accuracy"
);

const accuracyData = await accuracyResponse.json();

if (accuracyData.accuracy !== undefined) {

    document.getElementById("forecast-accuracy").textContent =
        accuracyData.accuracy.toFixed(1) + "%";

}

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/forecast-data"
        );

        const forecastData = await response.json();

        console.log("Forecast KPI Data:", forecastData);


        // ===============================
        // NEXT MONTH SALES
        // ===============================

        if (forecastData.length > 0) {

            const nextMonth =
                Number(forecastData[0].Predicted_Sales);

            document.getElementById("next-month-sales").textContent =
                "₹" + nextMonth.toLocaleString("en-IN");

        }


        // ===============================
        // PREDICTION PERIOD
        // ===============================

        document.getElementById("prediction-period").textContent =
            forecastData.length + " Months";


        // ===============================
        // GROWTH RATE
        // ===============================

        const monthlyResponse = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/monthly-sales"
        );

        const monthlyData = await monthlyResponse.json();


        if (
            monthlyData.length > 0 &&
            forecastData.length > 0
        ) {

            const lastActual =
                Number(
                    monthlyData[monthlyData.length - 1].sales
                );

            const nextForecast =
                Number(
                    forecastData[0].Predicted_Sales
                );

            const growth =
                ((nextForecast - lastActual) / lastActual) * 100;


            document.getElementById("growth-rate").textContent =
                (growth >= 0 ? "+" : "") +
                growth.toFixed(1) +
                "%";

        }


    } catch (error) {

        console.log(
            "Forecast KPI Error:",
            error
        );

    }

}

loadForecastKPIs();

async function loadCustomerKPIs() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/customer-kpis"
        );

        const data = await response.json();

        console.log("Customer KPIs:", data);

        document.getElementById("totalCustomers").textContent =
            Number(data.total_customers).toLocaleString("en-IN");

        document.getElementById("newCustomers").textContent =
            Number(data.new_customers).toLocaleString("en-IN");

        document.getElementById("repeatCustomers").textContent =
            Number(data.repeat_customers).toLocaleString("en-IN");

    }
    catch (error) {

        console.log(
            "Customer KPI Error:",
            error
        );

    }

}

loadCustomerKPIs();

let customersRegionChart = null;

async function loadRegionKPIs() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/region-kpis"
        );

        const data = await response.json();

        console.log("Region KPIs:", data);

        document.getElementById("bestRegion").textContent =
            data.best_region;

        document.getElementById("totalRegions").textContent =
            data.total_regions;

        document.getElementById("highestRegionSales").textContent =
            "₹" + Number(data.highest_sales).toLocaleString("en-IN", {
                maximumFractionDigits: 0
            });

        document.getElementById("highestRegionProfit").textContent =
            "₹" + Number(data.highest_profit).toLocaleString("en-IN", {
                maximumFractionDigits: 0
            });

    }
    catch (error) {

        console.log(
            "Region KPI Error:",
            error
        );

    }

}

loadRegionKPIs();

async function loadSalesKPIs() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/sales-kpis"
        );

        const data = await response.json();

        console.log("Sales KPIs:", data);

        document.getElementById("salesTotal").textContent =
            "₹" + Number(data.total_sales).toLocaleString("en-IN", {
                maximumFractionDigits: 0
            });

        document.getElementById("profitTotal").textContent =
            "₹" + Number(data.total_profit).toLocaleString("en-IN", {
                maximumFractionDigits: 0
            });

        document.getElementById("ordersTotal").textContent =
            Number(data.total_orders).toLocaleString("en-IN");

        document.getElementById("discountAverage").textContent =
            (Number(data.average_discount) * 100).toFixed(1) + "%";

    }
    catch (error) {

        console.log(
            "Sales KPI Error:",
            error
        );

    }

}

loadSalesKPIs();

async function loadBusinessInsights() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/business-insights"
        );

        const data = await response.json();

        console.log("Business Insights:", data);

        const list =
            document.getElementById("businessInsightsList");

        if (!list) return;

        list.innerHTML = "";

        if (data.error) {

            list.innerHTML =
                `<li>Unable to load business insights.</li>`;

            return;
        }

        data.insights.forEach(insight => {

            const li = document.createElement("li");

            li.textContent = insight;

            list.appendChild(li);

        });

    }
    catch (error) {

        console.log(
            "Business Insights Error:",
            error
        );

    }

}

loadBusinessInsights();

async function loadCustomersRegionChart() {

    try {

        const response = await fetch(
            "https://sales-analysis-and-forecating.onrender.com/analysis/customers-by-region"
        );

        const data = await response.json();

        console.log("Customers by Region:", data);

        const labels = data.map(item => item.Region);

        const customers = data.map(item => Number(item.customers));

        console.log("Region Labels:", labels);
        console.log("Region Customers:", customers);

        const canvas = document.getElementById(
            "customerRegionChart"
        );

        if (!canvas) {
            console.log("customerRegionChart not found");
            return;
        }

        new Chart(canvas, {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{

                    label: "Customers",

                    data: customers,

                    backgroundColor: "#06b6d4",

                    borderRadius: 8

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    x: {

                        ticks: {
                            color: "#ffffff"
                        },

                        grid: {
                            display: false
                        }

                    },

                    y: {

                        beginAtZero: true,

                        ticks: {
                            color: "#ffffff"
                        }

                    }

                }

            }

        });

    }
    catch (error) {

        console.error(
            "Customers Region Chart Error:",
            error
        );

    }

}

const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {
    logoutBtn.addEventListener("click", function () {

        localStorage.removeItem("session_token");
        localStorage.removeItem("user_email");

        window.location.href = "login.html";

    });
}

document
    .getElementById("downloadSalesAnalysisPDF")
    .addEventListener("click", () => {

        window.open(
            "https://sales-analysis-and-forecating.onrender.com/reports/sales-analysis-pdf",
            "_blank"
        );

    });

document.getElementById("downloadRegionPDF").addEventListener("click", () => {

    window.open(
        "https://sales-analysis-and-forecating.onrender.com/reports/region-pdf",
        "_blank"
    );

});


document.getElementById("downloadDashboardPDF").addEventListener("click", () => {
    window.open(
        "https://sales-analysis-and-forecating.onrender.com/reports/dashboard-pdf",
        "_blank"
    );
});

document
    .getElementById("downloadProductPDF")
    .addEventListener("click", () => {

        window.open(
            "https://sales-analysis-and-forecating.onrender.com/reports/products-pdf",
            "_blank"
        );

    });

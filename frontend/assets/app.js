new Vue({
    el: '#app',
    data: {
        products: [],
        orders: [],
        customers: [],
        productName: '',
        productPrice: '',
        orderCustomer: '',
        orderProduct: '',
        orderQuantity: '',
        customerName: '',
        customerEmail: ''
    },
    mounted() {
        this.fetchProducts();
        this.fetchOrders();
        this.fetchCustomers();
    },
    methods: {
        fetchProducts() {
            fetch('/products').then(res => res.json()).then(data => {
                this.products = data;
            });
        },
        fetchOrders() {
            fetch('/orders').then(res => res.json()).then(data => {
                this.orders = data;
            });
        },
        fetchCustomers() {
            fetch('/customers').then(res => res.json()).then(data => {
                this.customers = data;
            });
        },
        addProduct(e) {
            e.preventDefault();
            fetch('/products', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: this.productName, price: this.productPrice })
            }).then(() => {
                this.productName = '';
                this.productPrice = '';
                this.fetchProducts();
            });
        },
        addOrder(e) {
            e.preventDefault();
            fetch('/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ customer: this.orderCustomer, product: this.orderProduct, quantity: this.orderQuantity })
            }).then(() => {
                this.orderCustomer = '';
                this.orderProduct = '';
                this.orderQuantity = '';
                this.fetchOrders();
            });
        },
        addCustomer(e) {
            e.preventDefault();
            fetch('/customers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: this.customerName, email: this.customerEmail })
            }).then(() => {
                this.customerName = '';
                this.customerEmail = '';
                this.fetchCustomers();
            });
        }
    }
});

document.getElementById('add-product-form').onsubmit = function(e) {
    app.addProduct(e);
};
document.getElementById('add-order-form').onsubmit = function(e) {
    app.addOrder(e);
};
document.getElementById('add-customer-form').onsubmit = function(e) {
    app.addCustomer(e);
};
document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const productGrid = document.getElementById('productGrid');
    const categoryFilterButtons = document.querySelectorAll('.category-list button');
    const supplierFilterButtons = document.querySelectorAll('.supplier-list button');
    const cartItemsList = document.getElementById('cartItems');
    const cartTotalSpan = document.getElementById('cartTotal');
    const proceedToPaymentBtn = document.getElementById('proceedToPaymentBtn');
    const allProductsDataElement = document.getElementById('allProductsData');

    // --- Data Storage ---
    // Parse the JSON data passed from Flask
    // Ensure this parse happens safely, or it could break the script.
    let allProducts = [];
    try {
        allProducts = JSON.parse(allProductsDataElement.textContent);
    } catch (e) {
        console.error("Error parsing allProductsData:", e);
        console.error("Content was:", allProductsDataElement.textContent);
        alert("There was an error loading product data. Please try refreshing.");
    }

    let currentFilteredProducts = [...allProducts]; // Start with all products
    let cart = []; // Array to hold items in the cart

    // --- Filter State ---
    let activeCategory = 'all';
    let activeSupplier = 'all';

    // --- Helper Function: Get Image URL based on Category/Product Name ---
    // (Keep this function exactly as it was)
    function getProductImageUrl(productName, category) {
        productName = productName.toLowerCase().replace(/ /g, '-').replace(/'/g, ''); // Clean name for filename
        category = category.toLowerCase().replace(/ & /g, '-').replace(/ /g, '-');

        const specificImages = {
            'potato': 'potato.png', 'onion': 'onion.png', 'tomato': 'tomato.png',
            'milk': 'milk.png', 'paneer': 'paneer.png',
            'cooking-oil': 'cooking-oil.png', 'butter': 'butter.png',
            'red-chilli-powder': 'red-chilli-powder.png', 'turmeric-powder': 'turmeric-powder.png',
            'paper-plates': 'paper-plates.png', 'disposable-cups': 'disposable-cups.png',
            'tomato-ketchup': 'tomato-ketchup.png', 'banana': 'banana.png',
            'green-chilli': 'green-chilli.png', 'coriander': 'coriander.png',
            'cauliflower': 'cauliflower.png', 'cabbage': 'cabbage.png',
            'spinach': 'spinach.png', 'brinjal': 'brinjal.png',
            'apple': 'apple.png', 'orange': 'orange.png',
            'chilli-sauce': 'chilli-sauce.png', 'soy-sauce': 'soy-sauce.png',
            'cumin-seeds': 'cumin-seeds.png', 'garam-masala': 'garam-masala.png',
            'food-containers': 'food-containers.png', 'napkins': 'napkins.png',
            'serving-spoons': 'serving-spoons.png', 'tray': 'tray.png'
        };
        if (specificImages[productName]) {
            return `/static/images/${specificImages[productName]}`;
        }

        const categoryImages = {
            'vegetables': 'vegetables.png', 'fruits': 'fruits.png', 'sauces': 'sauces.png',
            'spices': 'spices.png', 'oil-butter': 'oil-butter.png',
            'packing-material': 'packing-material.png', 'serving-material': 'serving-material.png',
            'dairy': 'dairy.png', 'grain-flour': 'grain-flour.png', 'herb': 'herb.png'
        };
        if (categoryImages[category]) {
            return `/static/images/${categoryImages[category]}`;
        }

        return `/static/images/default.png`; // Generic fallback image
    }

    // --- Core Functions ---

    function renderProducts(productsToRender) {
        productGrid.innerHTML = ''; // Clear existing products
        if (productsToRender.length === 0) {
            productGrid.innerHTML = '<p>No products found for the current filters.</p>';
            return;
        }

        productsToRender.forEach(item => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            const imageUrl = getProductImageUrl(item.product_name, item.category);

            // Ensure all data attributes are correctly set from the 'item' object
            productCard.innerHTML = `
                <img src="${imageUrl}" alt="${item.product_name}">
                <h4>${item.product_name}</h4>
                <p>${item.category}</p>
                <div class="supplier-info">By: ${item.shop_business_name}</div>
                <div class="price">Rs. ${item.price_per_unit.toFixed(2)} / ${item.unit}</div>
                <div class="quantity-controls">
                    <input type="number"
                           min="0.1" step="0.1"
                           value="0"
                           class="quantity-input"
                           data-supplier-id="${item.supplier_id}"
                           data-product-id="${item.product_id}"
                           data-price-per-unit="${item.price_per_unit}"
                           data-product-name="${item.product_name}"
                           data-supplier-name="${item.shop_business_name}"
                           data-unit="${item.unit}"  >
                </div>
                <button type="button" class="btn add-to-cart-btn">Add to Cart</button>
            `;
            productGrid.appendChild(productCard);
        });

        // Attach event listeners to newly rendered 'Add to Cart' buttons
        // This is crucial because products are rendered dynamically.
        document.querySelectorAll('.add-to-cart-btn').forEach(button => {
            button.addEventListener('click', handleAddToCart);
        });
    }

    function applyFilters() {
        currentFilteredProducts = allProducts.filter(product => {
            const matchesCategory = activeCategory === 'all' || product.category === activeCategory;
            // Ensure supplier_id is compared as a string if data-filter-supplier is string
            const matchesSupplier = activeSupplier === 'all' || String(product.supplier_id) === activeSupplier;
            return matchesCategory && matchesSupplier;
        });
        renderProducts(currentFilteredProducts);
    }

    function handleAddToCart(event) {
        const productCard = event.target.closest('.product-card');
        const quantityInput = productCard.querySelector('.quantity-input');
        const quantity = parseFloat(quantityInput.value);

        if (quantity <= 0 || isNaN(quantity)) {
            alert('Please enter a valid quantity greater than zero.');
            return;
        }

        // Collect all necessary data from data-attributes of the input field
        const itemData = {
            supplier_id: parseInt(quantityInput.dataset.supplierId),
            product_id: parseInt(quantityInput.dataset.productId),
            price_per_unit: parseFloat(quantityInput.dataset.pricePerUnit),
            product_name: quantityInput.dataset.productName,
            supplier_name: quantityInput.dataset.supplierName,
            unit: quantityInput.dataset.unit,
            quantity: quantity
        };

        // Check if item already exists in cart from the same supplier for the exact same product
        const existingItemIndex = cart.findIndex(item =>
            item.supplier_id === itemData.supplier_id && item.product_id === itemData.product_id
        );

        if (existingItemIndex > -1) {
            cart[existingItemIndex].quantity += itemData.quantity; // Update quantity
        } else {
            cart.push(itemData);
        }
        quantityInput.value = 0; // Reset input field after adding
        updateCartDisplay();
    }

    function updateCartDisplay() {
        cartItemsList.innerHTML = ''; // Clear current display
        let total = 0;

        if (cart.length === 0) {
            cartItemsList.innerHTML = '<li>Your cart is empty.</li>';
            cartTotalSpan.textContent = '0.00';
            proceedToPaymentBtn.disabled = true; // Disable payment if cart is empty
            return;
        }

        proceedToPaymentBtn.disabled = false; // Enable payment if cart has items

        cart.forEach((item, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div class="cart-item-info">
                    ${item.product_name} (${item.quantity} ${item.unit} @ Rs.${item.price_per_unit.toFixed(2)})
                    <br>
                    <small>From: ${item.supplier_name}</small>
                </div>
                <button type="button" class="remove-item-btn" data-index="${index}">&times;</button>
            `;
            cartItemsList.appendChild(li);
            total += item.quantity * item.price_per_unit;
        });
        cartTotalSpan.textContent = total.toFixed(2);

        // Attach event listeners for remove buttons (crucial as these are dynamic)
        document.querySelectorAll('.remove-item-btn').forEach(button => {
            button.addEventListener('click', (event) => {
                const indexToRemove = parseInt(event.target.dataset.index);
                cart.splice(indexToRemove, 1); // Remove item from cart array
                updateCartDisplay();
            });
        });
    }

    async function handlePlaceOrder() {
        if (cart.length === 0) {
            alert('Your cart is empty. Please add items before placing an order.');
            return;
        }

        const suppliersInCart = [...new Set(cart.map(item => item.supplier_id))];

        if (suppliersInCart.length > 1) {
            alert('Your cart contains items from multiple suppliers. Please create separate orders for each supplier by clearing your cart and placing orders one supplier at a time.');
            return;
        }

        try {
            const response = await fetch('/api/place_order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(cart)
            });

            const result = await response.json();

            if (result.success) {
                alert(result.message + "\nOrder ID: " + result.order_id);
                cart = []; // Clear cart after successful order
                updateCartDisplay();
                window.location.href = '/my_orders'; // Redirect to my orders page
            } else {
                alert('Error placing order: ' + result.message);
            }
        } catch (error) {
            console.error('Network or server error:', error);
            alert('An unexpected error occurred. Please try again.');
        }
    }


    // --- Event Listeners Initialization ---

    // Category Filter Buttons
    categoryFilterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove 'active' class from all category buttons
            categoryFilterButtons.forEach(btn => btn.classList.remove('active'));
            // Add 'active' class to the clicked button
            button.classList.add('active');
            activeCategory = button.dataset.filterCategory;
            applyFilters();
        });
    });

    // Supplier Filter Buttons
    supplierFilterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove 'active' class from all supplier buttons
            supplierFilterButtons.forEach(btn => btn.classList.remove('active'));
            // Add 'active' class to the clicked button
            button.classList.add('active');
            activeSupplier = button.dataset.filterSupplier;
            applyFilters();
        });
    });

    // Proceed to Payment Button
    proceedToPaymentBtn.addEventListener('click', handlePlaceOrder);


    // --- Initial Render Calls ---
    applyFilters(); // Render all products initially when the page loads
    updateCartDisplay(); // Initialize cart display
});
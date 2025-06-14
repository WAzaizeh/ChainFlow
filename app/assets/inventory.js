// Quantity adjustment functions
function incrementQuantity() {
    const input = document.getElementById('quantity');
    input.value = parseInt(input.value) + 1;
}

function decrementQuantity() {
    const input = document.getElementById('quantity');
    const newValue = parseInt(input.value) - 1;
    if (newValue >= 1) {
        input.value = newValue;
    }
}

// Handle form success
document.addEventListener('DOMContentLoaded', function() {
    // Check if HTMX is loaded
    if (typeof htmx === 'undefined') {
        console.error('HTMX is not loaded');
        return;
    }
    console.log('HTMX is loaded');

    // Debug HTMX events
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        const targetId = event.detail.target.id;
        console.log(`HTMX Request Starting for ${targetId}:`, event.detail);
        
        // Only handle quantity form submissions
        if (targetId === 'quantity-form') {
            // Show loading state
            const submitButton = event.detail.target.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Updating...';
            }
        }
    });

    document.body.addEventListener('htmx:afterRequest', function(event) {
        const targetId = event.detail.target.id;
        console.log(`HTMX Request Complete for ${targetId}:`, event.detail);
        
        if (targetId === 'quantity-form' && event.detail.successful) {
            // Show success message
            const successMessage = document.getElementById('success-message');
            if (successMessage) {
                successMessage.classList.add('show');
                setTimeout(() => {
                    successMessage.classList.remove('show');
                }, 2000);
            }
            
            // Reset form and search
            const searchForm = document.getElementById('search-form');
            const itemForm = document.getElementById('item-form');
            
            if (searchForm) searchForm.reset();
            if (itemForm) itemForm.innerHTML = '';
        }
    });
    // Handle tab switching
    const tabs = document.querySelectorAll('input[name="inventory_tabs"]');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach((tab, index) => {
        tab.addEventListener('change', () => {
            tabContents.forEach(content => content.classList.add('hidden'));
            tabContents[index].classList.remove('hidden');
        });
    });
});

function updateConversionLabel(input) {
    const container = input.closest('.unit-input-container');
    const secondaryUnit = input.value || '[secondary unit]';
    const primaryUnit = document.querySelector('input[name="unit_name_0"]').value || '[primary unit]';
    
    const label = container.querySelector('.conversion-label');
    if (label) {
        label.textContent = `How many ${secondaryUnit}s in one ${primaryUnit}?`;
    }
}
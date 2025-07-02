function toggleTypeDropdown(orderId) {
    const dropdown = document.getElementById(`type-dropdown-${orderId}`);
    const arrow = document.getElementById(`type-arrow-${orderId}`);
    
    // Close all other dropdowns first
    document.querySelectorAll('[id^="type-dropdown-"]').forEach(d => {
        if (d.id !== `type-dropdown-${orderId}`) {
            d.classList.add('hidden');
            const otherArrow = document.getElementById(`type-arrow-${d.id.split('-').pop()}`);
            otherArrow?.classList.remove('rotate-180');
        }
    });
    
    // Toggle current dropdown
    dropdown.classList.toggle('hidden');
    arrow.classList.toggle('rotate-180');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
    if (!e.target.closest('.relative')) {
        document.querySelectorAll('[id^="type-dropdown-"]').forEach(d => {
            d.classList.add('hidden');
        });
        document.querySelectorAll('[id^="type-arrow-"]').forEach(a => {
            a.classList.remove('rotate-180');
        });
    }
});

// Handle successful type update
htmx.on('htmx:afterSwap', function(evt) {
    if (evt.target.id.startsWith('type-dropdown-')) {
        const orderId = evt.target.id.split('-').pop();
        const arrow = document.getElementById(`type-arrow-${orderId}`);
        arrow?.classList.remove('rotate-180');
    }
});
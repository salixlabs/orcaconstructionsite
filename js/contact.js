document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contactForm');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Basic form validation
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const projectType = document.getElementById('projectType').value;
        const message = document.getElementById('message').value.trim();
        
        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Please enter a valid email address');
            return;
        }
        
        // Validate phone format (optional field)
        if (phone && !/^\+?[\d\s-()]+$/.test(phone)) {
            alert('Please enter a valid phone number');
            return;
        }
        
        // For now, just show a success message
        // In a real implementation, this would send the data to a server
        alert('Thank you for your message! We will get back to you soon.');
        form.reset();
    });
    
    // Add focus styles to form elements
    const formInputs = form.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });
}); 
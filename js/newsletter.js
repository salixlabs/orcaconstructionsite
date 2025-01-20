// ConvertKit form handling
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.newsletter-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = form.querySelector('input[type="email"]').value;
            const submitButton = form.querySelector('button[type="submit"]');
            const statusMessage = form.querySelector('.form-status');
            
            // Disable the submit button and show loading state
            submitButton.disabled = true;
            submitButton.textContent = 'Subscribing...';
            
            try {
                // Replace YOUR_FORM_ID with your actual ConvertKit form ID
                const response = await fetch('https://api.convertkit.com/v3/forms/YOUR_FORM_ID/subscribe', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        api_key: 'YOUR_PUBLIC_API_KEY', // Replace with your ConvertKit public API key
                        email: email
                    })
                });

                const data = await response.json();
                
                if (response.ok) {
                    // Success message
                    if (statusMessage) {
                        statusMessage.textContent = 'Thank you for subscribing!';
                        statusMessage.className = 'form-status success';
                    }
                    form.reset();
                } else {
                    throw new Error(data.message || 'Subscription failed');
                }
            } catch (error) {
                // Error message
                if (statusMessage) {
                    statusMessage.textContent = 'Sorry, there was an error. Please try again.';
                    statusMessage.className = 'form-status error';
                }
                console.error('Newsletter subscription error:', error);
            } finally {
                // Reset button state
                submitButton.disabled = false;
                submitButton.textContent = 'Subscribe';
            }
        });
    });
}); 
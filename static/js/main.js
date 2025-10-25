// Main JavaScript for BanglaChatPro

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('BanglaChatPro loaded successfully!');

    // Add any global JavaScript functionality here

    // Example: Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
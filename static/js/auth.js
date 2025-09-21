document.addEventListener('DOMContentLoaded', function() {
    // Password strength indicator
    const passwordInput = document.getElementById('password');
    const strengthBar = document.getElementById('password-strength');
    const strengthText = document.getElementById('password-strength-text');
    
    if (passwordInput && strengthBar && strengthText) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            
            // Length check
            if (password.length >= 8) strength += 1;
            
            // Contains lowercase
            if (/[a-z]/.test(password)) strength += 1;
            
            // Contains uppercase
            if (/[A-Z]/.test(password)) strength += 1;
            
            // Contains numbers
            if (/[0-9]/.test(password)) strength += 1;
            
            // Contains special characters
            if (/[^A-Za-z0-9]/.test(password)) strength += 1;
            
            // Update strength indicator
            if (password.length === 0) {
                strengthBar.className = 'strength-fill';
                strengthBar.style.width = '0%';
                strengthText.className = '';
                strengthText.textContent = '';
            } else if (strength <= 2) {
                strengthBar.className = 'strength-fill weak';
                strengthText.className = 'weak';
                strengthText.textContent = 'Weak';
            } else if (strength <= 4) {
                strengthBar.className = 'strength-fill medium';
                strengthText.className = 'medium';
                strengthText.textContent = 'Medium';
            } else {
                strengthBar.className = 'strength-fill strong';
                strengthText.className = 'strong';
                strengthText.textContent = 'Strong';
            }
        });
    }
    
    // Password confirmation validation
    const confirmPasswordInput = document.getElementById('confirm_password');
    
    if (passwordInput && confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', function() {
            if (passwordInput.value !== this.value) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    // Form validation
    const registerForm = document.querySelector('form[action="{{ url_for(\'register\') }}"]');
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            
            if (password && confirmPassword && password.value !== confirmPassword.value) {
                e.preventDefault();
                alert('Passwords do not match. Please check and try again.');
                confirmPassword.focus();
            }
            
            // Additional validation can be added here
        });
    }
    
    // Social login buttons (placeholder functionality)
    const socialButtons = document.querySelectorAll('.btn-social');
    
    socialButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const provider = this.classList.contains('btn-google') ? 'Google' : 'Facebook';
            alert(`${provider} login integration would be implemented here. This is a demo.`);
        });
    });
    
    // Forgot password functionality
    const forgotPasswordLink = document.querySelector('.forgot-password');
    
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Password reset functionality would be implemented here. This is a demo.');
        });
    }
    
    // Terms and privacy links
    const termsLinks = document.querySelectorAll('a[href="#"]');
    
    termsLinks.forEach(link => {
        if (link.textContent.includes('Terms') || link.textContent.includes('Privacy')) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const isTerms = link.textContent.includes('Terms');
                alert(`${isTerms ? 'Terms of Service' : 'Privacy Policy'} would be displayed here. This is a demo.`);
            });
        }
    });
});
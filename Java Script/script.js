document.addEventListener('DOMContentLoaded', () => {

    const signupForm = document.getElementById('signupForm');
    const loginForm = document.getElementById('loginForm');
    const resetForm = document.getElementById('resetForm');
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    document.body.appendChild(overlay);

    // Get elements for signup form
    const username = document.getElementById('username');
    const phone = document.getElementById('phone');
    const emailSignup = document.getElementById('email');
    const passwordSignup = document.getElementById('password');

    // Get elements for login form
    const emailLogin = document.getElementById('email1');
    const passwordLogin = document.getElementById('password1');

    // Get elements for reset password form
    const emailReset = document.getElementById('email2');

    // Header buttons
    const signUpButton = document.querySelector('.sign-up');
    const loginButton = document.querySelector('.log-in');

    // Links inside forms
    const forgotPasswordLinks = document.querySelectorAll('.page-links'); // All links with class "page-links"

    // Hide all forms initially
    const hideAllForms = () => {
        signupForm.style.display = 'none';
        loginForm.style.display = 'none';
        resetForm.style.display = 'none';
        overlay.style.display = 'none';
    };

    const showForm = (form) => {
        hideAllForms(); // Ensure no other form is visible
        form.style.display = 'block'; // Show the requested form
        overlay.style.display = 'block'; // Show overlay
        resetErrors(form); // Reset errors when switching forms
    };

    // Function to reset errors when reopening a form
    const resetErrors = (form) => {
        const errorDivs = form.querySelectorAll('.error-message');
        errorDivs.forEach(errorDiv => {
            errorDiv.innerText = ''; // Clear error message
        });

        const formGroup = form.querySelectorAll('.error');
        formGroup.forEach(eachFormGroup => {
            eachFormGroup.classList.remove('error'); // Remove error class
            eachFormGroup.querySelector("input").style.borderColor = ""; // Reset border color
        });
    };

    // Event listeners for page links
    forgotPasswordLinks.forEach((link) => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const linkText = e.target.textContent.trim();

            if (linkText === 'Forgot Password?') {
                showForm(resetForm);
            } else if (linkText === 'Login') {
                showForm(loginForm);
            } else if (linkText === 'Sign up') {
                showForm(signupForm);
            }
        });
    });

    // Hide forms and overlay when clicking outside the form
    overlay.addEventListener('click', hideAllForms);

    hideAllForms(); // Hide all forms on load

    // Event listeners for showing forms based on button clicks
    signUpButton.addEventListener('click', (e) => {
        e.preventDefault();
        showForm(signupForm);
    });

    loginButton.addEventListener('click', (e) => {
        e.preventDefault();
        showForm(loginForm);
    });

    // Link inside forms to toggle between them
    document.querySelectorAll('.page-links').forEach((link) => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const linkText = e.target.textContent.trim();
            document.querySelectorAll("form").forEach(function(form){
                resetErrors(form); // Reset errors for all forms
            });
            if (linkText === 'Sign up') {
                showForm(signupForm);
            } else if (linkText === 'Login') {
                showForm(loginForm);
            } else if (linkText.includes('Forgot password')) {
                showForm(resetForm);
            }
        });
    });

    // Close forms and overlay when pressing the "Escape" key
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            hideAllForms();
        }
    });

    // Event listeners for signup, login, and reset forms
    [username, phone, emailSignup, passwordSignup].forEach((input) => {
        input.addEventListener('input', () => {
            clearError(input); // Clear error message while typing
        });
        input.addEventListener('blur', () => {
            validateField(input); // Validate on blur to show error if needed
        });
    });

    [emailLogin, passwordLogin, emailReset].forEach((input) => {
        input.addEventListener('input', () => {
            clearError(input); // Clear error message while typing
        });
        input.addEventListener('blur', () => {
            validateField(input); // Validate on blur to show error if needed
        });
    });

    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (validateInputsSignup()) {
            try {
                const response = await fetch('/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: username.value.trim(),
                        email: emailSignup.value.trim(),
                        phone: phone.value.trim(),
                        password: passwordSignup.value.trim()
                    })
                });
    
                const data = await response.json();
    
                if (response.ok) {
                    localStorage.setItem('token', data.token);
                    alert('Signup successful!');
                    hideAllForms();
                    // Optional: Redirect or update UI
                } else {
                    alert(data.error || 'Signup failed');
                }
            } catch (error) {
                console.error('Signup error:', error);
                alert('An error occurred during signup');
            }
        }
    });
    
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (validateInputsLogin()) {
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: emailLogin.value.trim(),
                        password: passwordLogin.value.trim()
                    })
                });
    
                const data = await response.json();
    
                if (response.ok) {
                    localStorage.setItem('token', data.token);
                    alert('Login successful!');
                    hideAllForms();
                    // Optional: Redirect or update UI
                } else {
                    alert(data.error || 'Login failed');
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('An error occurred during login');
            }
        }
    });
    resetForm.addEventListener('submit', (e) => {
        e.preventDefault(); // Prevent default form submission
        if (validateInputsReset()) {
            alert('Reset link sent to your email!');
        }
    });

    // Clear error messages
    const clearError = (element) => {
        const parent = element.parentElement;
        const errorDisplay = parent.querySelector('.error-message');
        errorDisplay.innerText = ''; // Clear error message
        parent.classList.remove('error');
        element.style.borderColor = ''; // Reset border color
    };

    // Set error and success styles
    const setError = (element, message) => {
        const parent = element.parentElement;
        const errorDisplay = parent.querySelector('.error-message');
        errorDisplay.innerText = message;
        parent.classList.add('error');
        parent.classList.remove('success');
        element.style.borderColor = 'red'; // Red border for error
    };

    const setSuccess = (element) => {
        const parent = element.parentElement;
        const errorDisplay = parent.querySelector('.error-message');
        errorDisplay.innerText = '';
        parent.classList.add('success');
        parent.classList.remove('error');
        element.style.borderColor = 'green'; // Green border for success
    };

    // Email validation
    const isValidEmail = (email) => {
        const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return re.test(String(email).toLowerCase());
    };

    // Validate fields for signup form
    const validateField = (input) => {
        const value = input.value.trim();
        switch (input.id) {
            case 'username':
                if (value === '') {
                    setError(input, 'Name is required');
                } else {
                    setSuccess(input);
                }
                break;
                case 'phone':
                    if (value === '') {
                        setError(input, 'Phone is required');
                    } else if (value.length < 10) {
                        setError(input, 'Phone must be a valid 10-digit number');
                    } else if (value.length > 10) {  // New check for phone number greater than 10 digits
                        setError(input, 'Phone number must not exceed 10 digits');
                    } else {
                        setSuccess(input);
                    }
                    break;
            case 'email':
                if (value === '') {
                    setError(input, 'Email is required');
                } else if (!isValidEmail(value)) {
                    setError(input, 'Provide a valid email address');
                } else {
                    setSuccess(input);
                }
                break;
            case 'password':
                if (value === '') {
                    setError(input, 'Password is required');
                } else if (value.length < 8) {
                    setError(input, 'Password must be at least 8 characters');
                } else {
                    setSuccess(input);
                }
                break;
        }
    };

    // Validate signup form inputs
    const validateInputsSignup = () => {
        const usernameValue = username.value.trim();
        const phoneValue = phone.value.trim();
        const emailSignupValue = emailSignup.value.trim();
        const passwordSignupValue = passwordSignup.value.trim();
        let isFormValid = true;

        if (usernameValue === '') {
            setError(username, 'Name is required');
            isFormValid = false;
        } else {
            setSuccess(username);
        }

        if (phoneValue === '') {
            setError(phone, 'Phone is required');
            isFormValid = false;
        } else if (phoneValue.length < 10) {
            setError(phone, 'Phone must be a valid 10-digit number');
            isFormValid = false;
        } else {
            setSuccess(phone);
        }

        if (emailSignupValue === '') {
            setError(emailSignup, 'Email is required');
            isFormValid = false;
        } else if (!isValidEmail(emailSignupValue)) {
            setError(emailSignup, 'Provide a valid email address');
            isFormValid = false;
        } else {
            setSuccess(emailSignup);
        }

        if (passwordSignupValue === '') {
            setError(passwordSignup, 'Password is required');
            isFormValid = false;
        } else if (passwordSignupValue.length < 8) {
            setError(passwordSignup, 'Password must be at least 8 characters');
            isFormValid = false;
        } else {
            setSuccess(passwordSignup);
        }

        return isFormValid;
    };

    // Validate login form inputs
    const validateInputsLogin = () => {
        const emailLoginValue = emailLogin.value.trim();
        const passwordLoginValue = passwordLogin.value.trim();
        let isFormValid = true;

        if (emailLoginValue === '') {
            setError(emailLogin, 'Email is required');
            isFormValid = false;
        } else if (!isValidEmail(emailLoginValue)) {
            setError(emailLogin, 'Provide a valid email address');
            isFormValid = false;
        } else {
            setSuccess(emailLogin);
        }

        if (passwordLoginValue === '') {
            setError(passwordLogin, 'Password is required');
            isFormValid = false;
        } else {
            setSuccess(passwordLogin);
        }

        return isFormValid;
    };

    // Validate reset password form inputs
    const validateInputsReset = () => {
        const emailResetValue = emailReset.value.trim();
        let isFormValid = true;

        if (emailResetValue === '') {
            setError(emailReset, 'Email is required');
            isFormValid = false;
        } else if (!isValidEmail(emailResetValue)) {
            setError(emailReset, 'Provide a valid email address');
            isFormValid = false;
        } else {
            setSuccess(emailReset);
        }

        return isFormValid;
    };

});






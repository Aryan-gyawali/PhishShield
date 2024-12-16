// Wait for the DOM to load
document.addEventListener('DOMContentLoaded', () => {
    // Select forms
    const signupForm = document.getElementById('signupForm');
    const loginForm = document.querySelector('.btn-cta2').closest('form');
    const forgotPasswordForm = document.querySelector('.btn-cta3').closest('form');

    // Input elements for signup form
    const nameInput = signupForm.querySelector('#name');
    const phoneInput = signupForm.querySelector('#phone');
    const emailInputSignup = signupForm.querySelector('#email');
    const passwordInputSignup = signupForm.querySelector('#password');

    // Input elements for login form
    const emailInputLogin = loginForm.querySelector('#email');
    const passwordInputLogin = loginForm.querySelector('#password');

    // Input element for forgot password form
    const emailInputForgotPassword = forgotPasswordForm.querySelector('#email');

    // Add event listeners for form submissions
    signupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        validateSignupForm();
    });

    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        validateLoginForm();
    });

    forgotPasswordForm.addEventListener('submit', (e) => {
        e.preventDefault();
        validateForgotPasswordForm();
    });

    // Function to set error message
    const setError = (element, message) => {
        const inputControl = element.parentElement;
        const errorDisplay = inputControl.querySelector('.error');

        if (!errorDisplay) {
            const newError = document.createElement('span');
            newError.classList.add('error');
            newError.style.color = 'red';
            newError.innerText = message;
            inputControl.appendChild(newError);
        } else {
            errorDisplay.innerText = message;
        }

        inputControl.classList.add('error');
        inputControl.classList.remove('success');
    };

    // Function to set success
    const setSuccess = (element) => {
        const inputControl = element.parentElement;
        const errorDisplay = inputControl.querySelector('.error');

        if (errorDisplay) {
            errorDisplay.innerText = '';
        }

        inputControl.classList.add('success');
        inputControl.classList.remove('error');
    };

    // Function to validate email format
    const isValidEmail = (email) => {
        const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    };

    // Function to validate the signup form
    const validateSignupForm = () => {
        const nameValue = nameInput.value.trim();
        const phoneValue = phoneInput.value.trim();
        const emailValue = emailInputSignup.value.trim();
        const passwordValue = passwordInputSignup.value.trim();

        if (nameValue === '') {
            setError(nameInput, 'Name is required');
        } else {
            setSuccess(nameInput);
        }

        if (phoneValue === '') {
            setError(phoneInput, 'Phone is required');
        } else if (!/^\d{10}$/.test(phoneValue)) {
            setError(phoneInput, 'Phone must be a valid 10-digit number');
        } else {
            setSuccess(phoneInput);
        }

        if (emailValue === '') {
            setError(emailInputSignup, 'Email is required');
        } else if (!isValidEmail(emailValue)) {
            setError(emailInputSignup, 'Provide a valid email address');
        } else {
            setSuccess(emailInputSignup);
        }

        if (passwordValue === '') {
            setError(passwordInputSignup, 'Password is required');
        } else if (passwordValue.length < 8) {
            setError(passwordInputSignup, 'Password must be at least 8 characters long');
        } else {
            setSuccess(passwordInputSignup);
        }
    };

    // Function to validate the login form
    const validateLoginForm = () => {
        const emailValue = emailInputLogin.value.trim();
        const passwordValue = passwordInputLogin.value.trim();

        if (emailValue === '') {
            setError(emailInputLogin, 'Email is required');
        } else if (!isValidEmail(emailValue)) {
            setError(emailInputLogin, 'Provide a valid email address');
        } else {
            setSuccess(emailInputLogin);
        }

        if (passwordValue === '') {
            setError(passwordInputLogin, 'Password is required');
        } else if (passwordValue.length < 8) {
            setError(passwordInputLogin, 'Password must be at least 8 characters long');
        } else {
            setSuccess(passwordInputLogin);
        }
    };

    // Function to validate the forgot password form
    const validateForgotPasswordForm = () => {
        const emailValue = emailInputForgotPassword.value.trim();

        if (emailValue === '') {
            setError(emailInputForgotPassword, 'Email is required');
        } else if (!isValidEmail(emailValue)) {
            setError(emailInputForgotPassword, 'Provide a valid email address');
        } else {
            setSuccess(emailInputForgotPassword);
        }
    };
});









// another code


const form = document.getElementById('signupForm');
const username = document.getElementById('username');
const phone = document.getElementById('phone');
const email = document.getElementById('email');
const password = document.getElementById('password');



// Add input event listeners to dynamically change the border color
[username, phone, email, password].forEach((input) => {
    input.addEventListener('input', () => {
        validateField(input); // Validate each field as the user types
    });
    input.addEventListener('blur', () => {
        validateField(input); // Validate on blur as well
    });
});



// Add submit event listener to the form
form.addEventListener('submit', (e) => {
    e.preventDefault(); // Prevent default form submission

    if (validateInputs()) {
        // If form is valid, proceed with form submission or other actions
        alert('Form submitted successfully!');
    }
});

const setError = (element, message) => {
    const parent = element.parentElement;
    const errorDisplay = parent.querySelector('.error');

    errorDisplay.innerText = message;
    parent.classList.add('error');
    parent.classList.remove('success');
    element.style.borderColor = 'red';
};

const setSuccess = (element) => {
    const parent = element.parentElement;
    const errorDisplay = parent.querySelector('.error');

    errorDisplay.innerText = '';
    parent.classList.add('success');
    parent.classList.remove('error');
    element.style.borderColor = 'green';
};

const isValidEmail = (email) => {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
};

const validateInputs = () => {
    const usernameValue = username.value.trim();
    const phoneValue = phone.value.trim();
    const emailValue = email.value.trim();
    const passwordValue = password.value.trim();

    let isFormValid = true;

    if (usernameValue === '') {
        setError(username, 'Name is required');
        isFormValid = false;
    } else {
        setSuccess(username)
        
    }

    if (phoneValue === '') {
        setError(phone, 'Phone is required');
        isFormValid = false;
    } else if (!/^\d{10}$/.test(phoneValue)) {
        setError(phone, 'Phone must be a valid 10-digit number');
        isFormValid = false;
    } else {
        setSuccess(phone);
    }

    if (emailValue === '') {
        setError(email, 'Email is required');
        isFormValid = false;
    } else if (!isValidEmail(emailValue)) {
        setError(email, 'Provide a valid email address');
        isFormValid = false;
    } else {
        setSuccess(email);
    }

    if (passwordValue === '') {
        setError(password, 'Password is required');
        isFormValid = false;
    } else if (passwordValue.length < 8) {
        setError(password, 'Password must be at least 8 characters');
        isFormValid = false;
    } else {
        setSuccess(password);
    }

    return isFormValid;
};




//another code

const form = document.getElementById('signupForm');
const username = document.getElementById('username');
const phone = document.getElementById('phone');
const email = document.getElementById('email');
const password = document.getElementById('password');

// Add input event listeners to hide error messages while typing
[username, phone, email, password].forEach((input) => {
    input.addEventListener('input', () => {
        clearError(input); // Hide error message while typing
    });
    input.addEventListener('blur', () => {
        validateField(input); // Validate on blur to show error if needed
    });
});

// Add submit event listener to the form
form.addEventListener('submit', (e) => {
    e.preventDefault(); // Prevent default form submission

    if (validateInputs()) {
        // If form is valid, proceed with form submission or other actions
        alert('Form submitted successfully!');
    }
});

// Clear error message while typing
const clearError = (element) => {
    const parent = element.parentElement;
    const errorDisplay = parent.querySelector('.error');
    errorDisplay.innerText = ''; // Clear the error message
    parent.classList.remove('error');
    element.style.borderColor = ''; // Reset border color
};

// Dynamic color change for error and success states
const setError = (element, message) => {
    const parent = element.parentElement;
    const errorDisplay = parent.querySelector('.error');
    errorDisplay.innerText = message;
    parent.classList.add('error');
    parent.classList.remove('success');
    element.style.borderColor = 'red'; // Change the border color to red on error
};

const setSuccess = (element) => {
    const parent = element.parentElement;
    const errorDisplay = parent.querySelector('.error');

    errorDisplay.innerText = '';
    parent.classList.add('success');
    parent.classList.remove('error');
    element.style.borderColor = 'green'; // Change the border color to green on success
};

// Check if email is valid
const isValidEmail = (email) => {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
};

// Validate individual fields and apply dynamic color changes
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
                // Only show this if the form is submitted with an incomplete phone number
                setError(input, 'Phone must be a valid 10-digit number');
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

// Overall form validation (called on form submission)
const validateInputs = () => {
    const usernameValue = username.value.trim();
    const phoneValue = phone.value.trim();
    const emailValue = email.value.trim();
    const passwordValue = password.value.trim();

    let isFormValid = true;

    // Username validation
    if (usernameValue === '') {
        setError(username, 'Name is required');
        isFormValid = false;
    } else {
        setSuccess(username);
    }

    // Phone validation (only show error after submitting the form)
    if (phoneValue === '') {
        setError(phone, 'Phone is required');
        isFormValid = false;
    } else if (phoneValue.length < 10) {
        setError(phone, 'Phone must be a valid 10-digit number');
        isFormValid = false;
    } else {
        setSuccess(phone);
    }

    // Email validation
    if (emailValue === '') {
        setError(email, 'Email is required');
        isFormValid = false;
    } else if (!isValidEmail(emailValue)) {
        setError(email, 'Provide a valid email address');
        isFormValid = false;
    } else {
        setSuccess(email);
    }

    // Password validation
    if (passwordValue === '') {
        setError(password, 'Password is required');
        isFormValid = false;
    } else if (passwordValue.length < 8) {
        setError(password, 'Password must be at least 8 characters');
        isFormValid = false;
    } else {
        setSuccess(password);
    }

    return isFormValid;
};











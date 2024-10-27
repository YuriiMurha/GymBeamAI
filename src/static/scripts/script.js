// Modal functionality
document.getElementById('loginBtn').addEventListener('click', () => {
    document.getElementById('loginModal').style.display = 'flex';
    document.getElementById('loginUsername').focus(); // Auto-focus on the username input
});

document.getElementById('registerBtn').addEventListener('click', () => {
    document.getElementById('registerModal').style.display = 'flex';
    document.getElementById('registerUsername').focus(); // Auto-focus on the username input
});

document.getElementById('loginClose').addEventListener('click', () => {
    document.getElementById('loginModal').style.display = 'none';
});

document.getElementById('registerClose').addEventListener('click', () => {
    document.getElementById('registerModal').style.display = 'none';
});

// Enhanced Modal close by clicking outside
window.onclick = function(event) {
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');

    if (event.target === loginModal) {
        loginModal.style.display = 'none';
    }
    if (event.target === registerModal) {
        registerModal.style.display = 'none';
    }
}

// "Database" of users (local list)
let users = [{ username: 'admin', password: 'admin' }];

// Login functionality
document.getElementById('submitLogin').addEventListener('click', () => {

    alert('Login successful!');
    document.getElementById('loginModal').style.display = 'none';
    document.getElementById('chatInput').disabled = false;
    document.getElementById('submitBtn').disabled = false;

    if (rememberMe) {
        localStorage.setItem('loggedInUser', username);
    }

    window.location.href = "dashboard.html";
});

// Registration functionality
document.getElementById('submitRegister').addEventListener('click', () => {
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('registerConfirmPassword').value;

    //if (username && password && confirmPassword && termsAccepted) {
        if (password !== confirmPassword) {
            showError('Passwords do not match.');
            return;
        }

        const userExists = false;// users.find(user => user.username === username);

        if (userExists) {
            showError('User already exists.');
        } else if (password.length < 6) {
            showError('Password is too short. It must be at least 6 characters.');
        } else {
            users.push({ username, password });
            showSuccess('Registration successful!');
            document.getElementById('registerModal').style.display = 'none';
        }
        
    window.location.href = "dashboard";
    //} else {
    //    showError('Please fill in all fields and accept the terms.');
    //}
});

// Error and Success Messages
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.classList.add('error-popup');
    errorDiv.innerText = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.classList.add('success-popup');
    successDiv.innerText = message;
    document.body.appendChild(successDiv);
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Alert when clicking on the entire form area if user is not logged in
document.getElementById('formArea').addEventListener('click', () => {
    if (document.getElementById('chatInput').disabled) {
        showError("Please register or log in to use this form.");
    }
});

// Alert when clicking inside form elements
document.querySelectorAll('.chat-input-container *').forEach(element => {
    element.addEventListener('click', (event) => {
        event.stopPropagation(); // Stop event from bubbling up
        if (document.getElementById('chatInput').disabled) {
            showError("Please register or log in to use this form.");
        }
    });
});

// Check for saved session
window.onload = function() {
    const loggedInUser = localStorage.getItem('loggedInUser');
    if (loggedInUser) {
        document.getElementById('chatInput').disabled = false;
        document.getElementById('submitBtn').disabled = false;
    }
};

// Заборона писати в полі "Write your message"
document.getElementById('chatInput').addEventListener('keydown', (event) => {
//    event.preventDefault(); // Блокуємо будь-які натискання клавіш
});

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('multiStepForm');
    const steps = Array.from(document.querySelectorAll('.step'));
    const progressSteps = Array.from(document.querySelectorAll('.progress-step'));
    let currentStep = 0;

    // Navigation buttons event listeners
    const nextButton = document.querySelector('button[data-direction="next"]');
    const submitButton = document.querySelector('button[data-direction="submit"]');

    function updateButtonVisibility() {
        if (currentStep === steps.length - 1) {
            nextButton.style.display = 'none';
            submitButton.style.display = 'inline-block';
        } else {
            nextButton.style.display = 'inline-block';
            submitButton.style.display = 'none';
        }
    }

    document.querySelectorAll('.form-navigation button').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const direction = e.target.dataset.direction;
            
            if (direction === 'next' && !validateStep(currentStep)) {
                return;
            }

            if (direction === 'next' && currentStep < steps.length - 1) {
                currentStep++;
            } else if (direction === 'prev' && currentStep > 0) {
                currentStep--;
            } else if (direction === 'submit') {
                if (validateStep(currentStep)) {
                    form.submit();
                    return;
                }
                return;
            }

            updateSteps();
            updateButtonVisibility();
        });
    });

    // Initialize button visibility on page load
    updateButtonVisibility();

    // Add education entry
    document.getElementById('addEducation')?.addEventListener('click', function() {
        const container = document.getElementById('educationContainer');
        const entryGroup = document.createElement('div');
        entryGroup.className = 'entry-group';
        entryGroup.innerHTML = `
            <label>Course Name:</label>
            <input type="text" name="course_name" required />

            <label>Institution Name:</label>
            <input type="text" name="institution_name" required />

            <label>From:</label>
            <input type="date" name="edu_from" required />

            <label>To:</label>
            <input type="date" name="edu_to" required />

            <button type="button" class="remove-btn" onclick="this.parentElement.remove()">Remove</button>
        `;
        container.appendChild(entryGroup);

        // Add animation
        entryGroup.style.opacity = '0';
        entryGroup.style.transform = 'translateY(20px)';
        setTimeout(() => {
            entryGroup.style.transition = 'all 0.3s ease';
            entryGroup.style.opacity = '1';
            entryGroup.style.transform = 'translateY(0)';
        }, 10);
    });

    // Add skill entry
    document.getElementById('addSkill')?.addEventListener('click', function() {
        const container = document.getElementById('skillsContainer');
        const entryGroup = document.createElement('div');
        entryGroup.className = 'entry-group';
        entryGroup.innerHTML = `
            <label>Skill:</label>
            <input type="text" name="skills" required />
            <button type="button" class="remove-btn" onclick="this.parentElement.remove()">Remove</button>
        `;
        container.appendChild(entryGroup);

        // Add animation
        entryGroup.style.opacity = '0';
        entryGroup.style.transform = 'translateY(20px)';
        setTimeout(() => {
            entryGroup.style.transition = 'all 0.3s ease';
            entryGroup.style.opacity = '1';
            entryGroup.style.transform = 'translateY(0)';
        }, 10);
    });

    // Validate each step
    function validateStep(stepIndex) {
        const currentStepElement = steps[stepIndex];
        const inputs = currentStepElement.querySelectorAll('input[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('error');
                showError(input, 'This field is required');
            } else {
                input.classList.remove('error');
                removeError(input);
            }
        });

        // Specific validation for email
        const emailInput = currentStepElement.querySelector('input[type="email"]');
        if (emailInput && emailInput.value) {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(emailInput.value)) {
                isValid = false;
                emailInput.classList.add('error');
                showError(emailInput, 'Please enter a valid email address');
            }
        }

        // Specific validation for phone
        const phoneInput = currentStepElement.querySelector('input[name="phone"]');
        if (phoneInput && phoneInput.value) {
            const phonePattern = /^\+?[1-9][0-9]{7,14}$/;
            if (!phonePattern.test(phoneInput.value)) {
                isValid = false;
                phoneInput.classList.add('error');
                showError(phoneInput, 'Please enter a valid phone number');
            }
        }

        return isValid;
    }

    // Show error message
    function showError(input, message) {
        let errorDiv = input.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains('error-message')) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            input.parentNode.insertBefore(errorDiv, input.nextSibling);
        }
        errorDiv.textContent = message;
        errorDiv.style.color = 'var(--danger-color)';
        errorDiv.style.fontSize = '0.875rem';
        errorDiv.style.marginTop = '-0.75rem';
        errorDiv.style.marginBottom = '0.75rem';
    }

    // Remove error message
    function removeError(input) {
        const errorDiv = input.nextElementSibling;
        if (errorDiv && errorDiv.classList.contains('error-message')) {
            errorDiv.remove();
        }
    }

    // Update steps visibility and progress
    function updateSteps() {
        steps.forEach((step, index) => {
            step.classList.remove('active');
            progressSteps[index].classList.remove('active', 'completed');
        });

        steps[currentStep].classList.add('active');
        progressSteps[currentStep].classList.add('active');

        // Update completed steps
        for (let i = 0; i < currentStep; i++) {
            progressSteps[i].classList.add('completed');
        }

        // Smooth scroll to top of form
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Add input event listeners for real-time validation
    document.querySelectorAll('input[required]').forEach(input => {
        input.addEventListener('input', function() {
            if (this.value.trim()) {
                this.classList.remove('error');
                removeError(this);
            }
        });
    });
});
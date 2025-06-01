document.addEventListener("DOMContentLoaded", function () {
    const profileForm = document.getElementById("profileEditForm");
    const editButton = document.getElementById("editProfileBtn");
    const saveButton = document.getElementById("saveProfileBtn");
    const inputs = document.querySelectorAll('form input:not([type="file"])');
    const fileInput = document.getElementById("profilePhoto");
    const changePhotoLabel = document.getElementById("changePhotoLabel");
    const csrfToken = profileForm.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    ).value;

    const togglePassword = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("password");
    const toggleConfirmPassword = document.getElementById(
        "toggleConfirmPassword"
    );
    const confirmPasswordInput = document.getElementById("confirm_password");

    const updateToggleButtonsState = () => {
        const areFieldsDisabled =
            passwordInput.disabled || confirmPasswordInput.disabled;
        togglePassword.style.pointerEvents = areFieldsDisabled
            ? "none"
            : "auto";
        togglePassword.style.opacity = areFieldsDisabled ? 0.5 : 1;
        toggleConfirmPassword.style.pointerEvents = areFieldsDisabled
            ? "none"
            : "auto";
        toggleConfirmPassword.style.opacity = areFieldsDisabled ? 0.5 : 1;
    };

    // Initial state: disable inputs and hide save button
    inputs.forEach((input) => (input.disabled = true));
    saveButton.style.display = "none";
    fileInput.style.display = "none"; // Initially hide file input
    changePhotoLabel.style.pointerEvents = "none";
    changePhotoLabel.style.opacity = 0.5;
    updateToggleButtonsState();

    editButton.addEventListener("click", function () {
        inputs.forEach((input) => (input.disabled = false));
        editButton.style.display = "none";
        saveButton.style.display = "inline-block";
        changePhotoLabel.style.pointerEvents = "auto"; // Enable label
        changePhotoLabel.style.opacity = "1"; // Make label fully visible
        updateToggleButtonsState();
    });

    // Handle form submission via fetch API
    profileForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent default form submission

        const password = document.getElementById("password").value;
        const confirmPassword =
            document.getElementById("confirm_password").value;

        // Password validation
        if (password && password !== confirmPassword) {
            alert("Passwords do not match!");
            return; // Stop execution if validation fails
        }

        const formData = new FormData(profileForm);
        formData.append("csrfmiddlewaretoken", csrfToken); // Explicitly append CSRF token

        fetch(profileForm.action, {
            method: "POST",
            body: formData,
        })
            .then((response) => {
                if (!response.ok) {
                    return response.json().then((err) => {
                        throw err;
                    });
                }
                return response.json();
            })
            .then((data) => {
                if (data.success) {
                    alert(data.message);
                    // Re-disable fields after successful submission
                    inputs.forEach((input) => (input.disabled = true));
                    editButton.style.display = "inline-block";
                    saveButton.style.display = "none";
                    fileInput.style.display = "none";
                    changePhotoLabel.style.pointerEvents = "none";
                    changePhotoLabel.style.opacity = 0.5;
                    updateToggleButtonsState();
                    // Optionally update UI elements that changed, e.g., profile image
                    if (data.photo_url) {
                        document.querySelector(".user_profile_img").src =
                            data.photo_url;
                        document.querySelector(".profile_img").src =
                            data.photo_url;
                    }
                } else {
                    alert(
                        data.message ||
                            "An error occurred during profile update."
                    );
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert(
                    "An error occurred: " +
                        (error.message || "Please try again.")
                );
            });
    });

    fileInput.addEventListener("change", function () {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.querySelector(".user_profile_img").src = e.target.result;
            document.querySelector(".profile_img").src = e.target.result; // Update nav bar image too
        };
        reader.readAsDataURL(fileInput.files[0]);
    });

    togglePassword.addEventListener("click", () => {
        if (passwordInput.disabled) return; // Prevent toggle if the field is disabled
        const isPasswordHidden = passwordInput.type === "password";
        passwordInput.type = isPasswordHidden ? "text" : "password";
        togglePassword.querySelector("img").src = isPasswordHidden
            ? window.OPEN_EYE_URL
            : window.CLOSE_EYE_URL;
    });

    toggleConfirmPassword.addEventListener("click", () => {
        if (confirmPasswordInput.disabled) return; // Prevent toggle if the field is disabled
        const isConfirmPasswordHidden =
            confirmPasswordInput.type === "password";
        confirmPasswordInput.type = isConfirmPasswordHidden
            ? "text"
            : "password";
        toggleConfirmPassword.querySelector("img").src = isConfirmPasswordHidden
            ? window.OPEN_EYE_URL
            : window.CLOSE_EYE_URL;
    });

    // Initialize the state of toggle buttons on page load
    updateToggleButtonsState();
});

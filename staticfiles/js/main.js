document.addEventListener("DOMContentLoaded", function () {
    const addPositionBtn = document.querySelector(".add-position-button");
    const addPositionModal = document.getElementById("addPositionModal");
    const closePositionModalBtn = document.querySelector(
        ".close-position-modal"
    );

    if (addPositionBtn && addPositionModal && closePositionModalBtn) {
        addPositionBtn.addEventListener("click", function () {
            addPositionModal.style.display = "block";
        });

        closePositionModalBtn.addEventListener("click", function () {
            addPositionModal.style.display = "none";
        });

        window.addEventListener("click", function (event) {
            if (event.target == addPositionModal) {
                addPositionModal.style.display = "none";
            }
        });
    }
});

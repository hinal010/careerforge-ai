document.addEventListener("DOMContentLoaded", function () {

    // ==============================
    // DELETE CONFIRMATION
    // ==============================
    window.confirmDelete = function (msg = "Are you sure?") {
        return confirm(msg);
    };

    // ==============================
    // PROFILE IMAGE PREVIEW
    // ==============================
    const photoInput = document.getElementById("photo");
    const previewImage = document.getElementById("photoPreview");

    if (photoInput && previewImage) {
        photoInput.addEventListener("change", function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImage.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // ==============================
    // EXPERIENCE PAGE LOGIC
    // ==============================
    const jobTitle = document.getElementById("job_title");
    const customJob = document.getElementById("customJobTitleGroup");
    const working = document.getElementById("currently_working");
    const endMonth = document.getElementById("end_month");

    function toggleJob() {
        if (!jobTitle || !customJob) return;
        customJob.style.display = jobTitle.value === "other" ? "block" : "none";
    }

    function toggleWorking() {
        if (!working || !endMonth) return;
        endMonth.disabled = working.checked;
        if (working.checked) endMonth.value = "";
    }

    if (jobTitle) {
        jobTitle.addEventListener("change", toggleJob);
        toggleJob();
    }

    if (working) {
        working.addEventListener("change", toggleWorking);
        toggleWorking();
    }

    // ==============================
    // SKILLS PAGE LOGIC
    // ==============================
    const jobRole = document.getElementById("job_role");
    const customRole = document.getElementById("customJobRoleGroup");

    if (jobRole && customRole) {
        jobRole.addEventListener("change", function () {
            customRole.style.display = jobRole.value === "other" ? "block" : "none";
        });
    }

});
window.onload = function () {
    document.getElementById("upload-button").addEventListener("click", () => {
        document.getElementById("upload-form").classList.remove("hide");
    });

    document.getElementById("cancel-upload").addEventListener("click", () => {
        document.getElementById("upload-form").classList.add("hide");
    });

    document.getElementById("new-folder").addEventListener("click", () => {
        document.getElementById("newfolder-form").classList.remove("hide");
    });

    document.getElementById("cancel-folder").addEventListener("click", () => {
        document.getElementById("newfolder-form").classList.add("hide");
    });
};
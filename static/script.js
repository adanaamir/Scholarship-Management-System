document.addEventListener("DOMContentLoaded", function () {
    const passwordField = document.getElementById("pass");
    const eyeOpen = document.getElementById("eyeopen");
    const eyeClose = document.getElementById("eyeclose"); 

    eyeOpen.addEventListener("click", () => {
        passwordField.type = "password";
        eyeOpen.style.display = "none";
        eyeClose.style.display = "inline";
    });

    eyeClose.addEventListener("click", () => {
        passwordField.type = "text";
        eyeClose.style.display = "none";
        eyeOpen.style.display = "inline";
    });
});

function toggleSelectBar() {
    var sidebar = document.getElementById("sidebar");
    if (sidebar.style.width == "250px"){
        sidebar.style.width = "0";  //hide the sidebar
    } else {
        sidebar.style.width = "250px";  //show it
    }
}

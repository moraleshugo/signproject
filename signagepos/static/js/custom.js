
// custom_script.js
document.addEventListener("DOMContentLoaded", function() {
    var alertElement = document.getElementById("success-alert");

    if (alertElement) {
        $("#success-alert").fadeTo(2000, 500).slideUp(500, function(){
            $("#success-alert").slideUp(500);
        });
    }
});


  

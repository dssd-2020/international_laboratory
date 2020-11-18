const showErrorAlert = () => {
    $("#alert-error").addClass("show");
}

const closeErrorAlert = () => {
    $("#alert-error > #error").text("Error");
    $("#alert-error").removeClass("show");
}
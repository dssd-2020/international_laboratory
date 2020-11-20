const showErrorAlert = (error) => {
    $("#alert-error > #error").text(error);
    $("#alert-error").addClass("show");
}

const closeErrorAlert = () => {
    $("#alert-error > #error").text("Error");
    $("#alert-error").removeClass("show");
}
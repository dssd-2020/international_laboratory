let activity_submit_button = $("#new-activity-submit");

activity_submit_button.click(
    () => {
        closeErrorAlert();

        let error;

        let name = $("input[name=activity-name]");
        name = name.val();
        (name.length) ?
            (name.length > 150) ?
                error = "El nombre de la actividad no puede contener más de 150 caracteres" :
                error = null :
            error = "El nombre de la actividad no puede estar vacío";

        (error) ? showErrorAlert(error) : createActivity(name);
    }
);

const createActivity = (name) => {
    activity_submit_button.prop("disabled", true);
    $.ajax({
        type: "POST",
        dataType: "json",
        data: {
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            name: name
        }
    }).done(
        (data) => {
            data["error"] ? showErrorAlert("Inténtelo nuevamente más tarde") : showSuccessModal();
        }
    ).fail(
        () => {
            showErrorAlert("Inténtelo nuevamente más tarde");
        }
    ).always(
        () => {
            activity_submit_button.prop("disabled", false);
        }
    );
};
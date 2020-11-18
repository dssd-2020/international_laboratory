$("#new-activity-submit").click(
    () => {
        closeErrorAlert();

        let error;

        let name = $("input[name=activity-name]");
        (name.val().length) ?
            (name.val().length > 150) ?
                error = "El nombre de la actividad no puede contener más de 150 caracteres" :
                error = null :
            error = "El nombre de la actividad no puede estar vacío";

        if (error) {
            $("#alert-error > #error").text(error);
            showErrorAlert();
        } else {
            $.ajax({
                type: "POST",
                url: "create_activity",
                data: {
                    "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
                    "name": name,
                },
                dataType: "json",
                success: (data) => {
                    console.log(data);
                }
            });
        }
    }
);
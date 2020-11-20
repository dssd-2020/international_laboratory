let protocol_submit_button = $("#new-protocol-submit");

protocol_submit_button.click(
    () => {
        closeErrorAlert();

        let error;
        let name;
        let start_date;
        let end_date;
        let order;
        let local;
        let points;
        let activities;

        name = $("input[name=protocol-name]");
        name = name.val();
        (name.length) ?
            (name.length > 150) ?
                error = "El nombre del protocolo no puede contener más de 150 caracteres" :
                error = null :
            error = "El nombre del protocolo no puede estar vacío";

        if (!error) {
            let today = new Date().toISOString().slice(0, 10);
            start_date = $("input[name=protocol-start-date]").val();
            end_date = $("input[name=protocol-end-date]").val();
            (start_date.length) ?
                (end_date.length) ?
                    (start_date >= today) ?
                        (end_date >= today) ?
                            (start_date > end_date) ?
                                error = "La fecha de inicio no puede ser posterior a la fecha de finalización" :
                                error = null :
                            error = "La fecha de finalización debe ser hoy o posterior" :
                        error = "La fecha de inicio debe ser hoy o posterior" :
                    error = "La fecha de finalización no puede estar vacía" :
                error = "La fecha de inicio no puede estar vacía";

            if (!error) {
                order = $("input[name=protocol-order]").val();
                (order.length) ?
                    (order > 0) ?
                        error = null :
                        error = "El orden de ejecución debe ser mayor que 0" :
                    error = "Debe indicarse un orden de ejecución";

                if (!error) {
                    local = $("select[name=protocol-local]").val();
                    (local) ?
                        (local === "0" || local === "1") ?
                            error = null :
                            error = "Debe seleccionarse una opción válida en el tipo de ejecución" :
                        error = "Debe seleccionarse un tipo de ejecución";

                    if (!error) {
                        points = $("input[name=protocol-points]").val();
                        (points.length) ?
                            (points > 0) ?
                                (points <= 100) ?
                                    error = null :
                                    error = "El puntaje debe ser menor que 100" :
                                error = "El puntaje debe ser mayor que 0" :
                            error = "Debe indicarse un puntaje";

                        if (!error) {
                            activities = $("select[name=protocol-activities]").val();
                            (activities.length) ?
                                error = null :
                                error = "Debe seleccionarse al menos una actividad"
                        }
                    }
                }
            }
        }

        (error) ? showErrorAlert(error) : createProtocol(name, start_date, end_date, order, local, points, activities);
    }
);

const createProtocol = (name, start_date, end_date, order, local, points, activities) => {
    protocol_submit_button.prop("disabled", true);
    $.ajax({
        type: "POST",
        dataType: "json",
        data: {
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            name: name,
            start_date: start_date,
            end_date: end_date,
            order: order,
            local: local,
            points: points,
            activities: activities,
            activities_length: activities.length
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
            protocol_submit_button.prop("disabled", false);
        }
    );
};
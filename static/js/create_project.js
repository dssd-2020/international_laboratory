let protocol_select = $("select[name=project-protocol]");
let responsible_select = $("select[name=project-responsible]");
let project_submit_button = $("#new-project-submit");
let protocol_add_button = $("#add-protocol-responsible");
let protocols = [];

protocol_add_button.click(
    () => {
        let protocol = protocol_select.val();
        let protocol_name = $("select[name=project-protocol] option:selected").text();
        let responsible = responsible_select.val();
        let responsible_name = $("select[name=project-responsible] option:selected").text();

        if (protocol && responsible) {
            protocols.push([protocol, responsible]);
            let index = protocols.length - 1

            protocol_select.val("");
            $(`select[name=project-protocol] option[value=${protocol}]`).wrap("<span/>");
            responsible_select.val("");

            $("#protocols-container").append(protocolResponsibleTemplate(index, protocol_name, responsible_name));
        }
    }
);

const protocolResponsibleTemplate = (index, protocol_name, responsible_name) => {
    return `
        <div id="protocol-responsible-${index}"
             class="form-row"
        >
            <div class="form-group col required">
                <label for="protocol-name-${index}"
                       class="province-font-medium"
                       hidden
                >
                    Protocolo
                </label>
                <input type="text"
                       id="protocol-name-${index}"
                       name="protocol-name-${index}"
                       class="form-control"
                       value="${protocol_name}"
                       readonly
                >
            </div>
            <div class="form-group col required">
                <label for="responsible-name-${index}"
                       class="province-font-medium"
                       hidden
                >
                    Protocolo
                </label>
                <input type="text"
                       id="responsible-name-${index}"
                       name="responsible-name-${index}"
                       class="form-control"
                       value="${responsible_name}"
                       readonly
                >
            </div>
            <div class="form-group col-2 text-center">
                <button type="button"
                        id="remove-protocol-responsible-${index}"
                        class="btn btn-secondary-white"
                        onclick="removeProtocolResponsible(${index})"
                >
                    <i class="fas fa-minus"></i>
                </button>
            </div>
        </div>
    `
};

const removeProtocolResponsible = (index) => {
    $(`select[name=project-protocol] option[value=${protocols[index][0]}]`).unwrap();
    $("#protocol-responsible-" + index).remove();
    protocols[index] = ["-1", "-1"];
};

project_submit_button.click(
    () => {
        closeErrorAlert();

        let error;
        let name;
        let start_date;
        let end_date;
        let project_manager = $("input[name=project-manager]").val();
        let active = ($("input[name=project-active]").prop("checked")) ? "1" : "0";
        let running_activity = $("input[name=running_activity]").val();

        name = $("input[name=project-name]");
        name = name.val();
        (name.length) ?
            (name.length > 150) ?
                error = "El nombre del proyecto no puede contener más de 150 caracteres" :
                error = null :
            error = "El nombre del proyecto no puede estar vacío";

        if (!error) {
            let today = new Date();
            today = today.getFullYear() + "-" + ("0"+(today.getMonth()+1)).slice(-2) + "-"+ ("0" + today.getDate()).slice(-2);

            start_date = $("input[name=project-start-date]").val();
            end_date = $("input[name=project-end-date]").val();
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
                (protocols.length) ?
                    error = null :
                    error = "Debe agregarse al menos un protocolo"
            }
        }

        (error) ? showErrorAlert(error) : createProject(name, start_date, end_date, project_manager, active, running_activity, protocols);
    }
);

const createProject = (name, start_date, end_date, project_manager, active, running_activity, protocols) => {
    project_submit_button.prop("disabled", true);
    $.ajax({
        type: "POST",
        dataType: "json",
        data: {
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            name: name,
            start_date: start_date,
            end_date: end_date,
            project_manager: project_manager,
            active: active,
            protocols: protocols,
            protocols_length: protocols.length,
            running_activity: running_activity
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
            project_submit_button.prop("disabled", false);
        }
    );
};
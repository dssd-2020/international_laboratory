let resolution_submit_button = $("#failure-resolution-submit");
let resolution;

const updateResolution = (resolution_id) => {
    let resolution_item = $(`#resolution-item-${resolution}`);
    let resolution_icon = $(`#resolution-icon-${resolution}`);

    if (resolution) {
        if (resolution_item.hasClass("btn-primary-blue")) {
            resolution_item.addClass("btn-secondary-white");
            resolution_item.removeClass("btn-primary-blue");
            resolution_icon.addClass("far fa-circle");
            resolution_icon.removeClass("fas fa-check-circle");
        }
    }

    resolution = resolution_id;

    resolution_item = $(`#resolution-item-${resolution_id}`);
    resolution_icon = $(`#resolution-icon-${resolution_id}`);

    if (resolution_item.hasClass("btn-secondary-white")) {
        resolution_item.addClass("btn-primary-blue");
        resolution_item.removeClass("btn-secondary-white");
        resolution_icon.addClass("fas fa-check-circle");
        resolution_icon.removeClass("far fa-circle");
    }
}

resolution_submit_button.click(
    () => {
        resolution_submit_button.prop("disabled", true);
        $.ajax({
            type: "POST",
            dataType: "json",
            data: {
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
                protocol: $("input[name=protocol]").val(),
                resolution: resolution,
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
                resolution_submit_button.prop("disabled", false);
            }
        );
    }
);
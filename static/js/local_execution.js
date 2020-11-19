let execution_submit_button = $("#local-execution-submit");
let activities = {};

const updateActivityExecution = (activity_id) => {
    let activity_item = $(`#activity-item-${activity_id}`);
    let activity_icon = $(`#activity-icon-${activity_id}`);
    if (activity_item.hasClass("btn-secondary-white")) {
        activity_item.addClass("btn-primary-blue");
        activity_item.removeClass("btn-secondary-white");
        activity_icon.addClass("fas fa-check-circle");
        activity_icon.removeClass("far fa-circle");
        activities[activity_id] = "1";
    } else if (activity_item.hasClass("btn-primary-blue")) {
        activity_item.addClass("btn-secondary-white");
        activity_item.removeClass("btn-primary-blue");
        activity_icon.addClass("far fa-circle");
        activity_icon.removeClass("fas fa-check-circle");
        delete activities[activity_id];
    }
}


execution_submit_button.click(
    () => {
        execution_submit_button.prop("disabled", true);
        $.ajax({
            type: "POST",
            dataType: "json",
            data: {
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
                protocol: $("input[name=protocol]").val(),
                activities: activities,
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
                execution_submit_button.prop("disabled", false);
            }
        );
    }
);
let notification_icon = $("#notification-icon");
let notification_count = $("#notification-count");

$(
    () => {
        checkNotifications();
        let check_notifications = setInterval(checkNotifications, 10000);
    }
);


const checkNotifications = () => {
    $.ajax(notifications_url, {
        type: "GET",
        dataType: "json",
        data: {
            "get_notifications_count": true
        }
    }).done(
        (data) => {
            if (data["notifications_count"]) {
                updateNotificationsCount(data["notifications_count"]);
            }
        }
    );
};

const updateNotificationsCount = (count) => {
    if (count) {
        notification_icon.addClass("fas").removeClass("far");
        notification_count.text(count);
    } else {
        notification_icon.addClass("far").removeClass("fas");
        notification_count.text("");
    }
}

const readNotification = (notification_id, next_step) => {
    let read_notification_submit_button = $(`#notification-action-${notification_id} span`);
    if (!read_notification_submit_button.hasClass("badge-disabled")) {
        read_notification_submit_button.addClass("badge-disabled");
        $.ajax({
            type: "POST",
            dataType: "json",
            data: {
                csrfmiddlewaretoken: $(`#notification-form-${notification_id} input[name=csrfmiddlewaretoken]`).val(),
                notification_id: notification_id
            }
        }).done(
            (data) => {
                if (!data["error"]) {
                    window.location.assign(next_step);
                }
            }
        ).always(
            () => {
                read_notification_submit_button.removeClass("badge-disabled");
            }
        );
    }
}
let notification_icon = $("#notification-icon");
let notification_count = $("#notification-count");

$(
    () => {
        checkNotifications();
        let check_notifications = setInterval(checkNotifications, 15000);
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
let logout_submit_button = $("#logout-submit");

logout_submit_button.click(
    () => logout()
);

const logout = () => {
    $.ajax(logout_url, {
        type: "GET",
        dataType: "json",
        data: {
            "logout": true
        }
    }).always(
        () => {
            window.location.assign("/");
        }
    );
};
let logout_submit_button = $("#logout-submit");

logout_submit_button.click(
    () => logout()
);

const logout = () => {
    $.ajax({
        type: "GET",
        dataType: "json",
        data: {
            "logout": true
        }
    }).always(
        () => {
            window.location.reload();
        }
    );
};
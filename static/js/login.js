let login_submit_button = $("#login-submit");

login_submit_button.click(
    () => {
        closeErrorAlert();

        let error;

        let username = $("input[name=username]");
        let password = $("input[name=password]");
        username = username.val();
        password = password.val();

        (username.length) ?
            (password.length) ?
                error = null :
                error = "Debe indicar una contraseña" :
            error = "Debe indicar un nombre de usuario";

        (error) ? showErrorAlert(error) : login(username, password);
    }
);

const login = (username, password) => {
    login_submit_button.prop("disabled", true);
    $.ajax({
        type: "POST",
        dataType: "json",
        data: {
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            username: username,
            password: password
        }
    }).done(
        (data) => {
            data["error"] ? showErrorAlert("Las credenciales ingresadas no son correctas") : showSuccessModal();
        }
    ).fail(
        () => {
            showErrorAlert("Inténtelo nuevamente más tarde");
        }
    ).always(
        () => {
            login_submit_button.prop("disabled", false);
        }
    );
};
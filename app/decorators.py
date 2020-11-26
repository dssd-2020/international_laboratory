from django.shortcuts import redirect


def login_required(function):
    def wrap(request, *args, **kwargs):
        session = args[0].session
        if "user_logged" in session and "bonita_cookies" in session:
            if "login" in function.__name__:
                return redirect("home")
            return function(request, *args, **kwargs)
        elif "login" in function.__name__:
            return function(request, *args, **kwargs)
        return redirect("login")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

from django.shortcuts import redirect


def login_required(function):
    def wrap(request, *args, **kwargs):
        session = args[0].session
        if "user_logged" in session and "bonita_cookies" in session:
            return function(request, *args, **kwargs)
        else:
            return redirect("home")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

import time

from api.models import UserPreferences

#Get current timestamp to use when serving static files

def current_timestamp():
    localtime = time.localtime()
    current_minute = localtime.tm_min
    current_second = localtime.tm_sec
    return f"{current_minute}{current_second}"


def timestamp(request):
    context = {"latest_timestamp": current_timestamp()}
    if request.user.is_authenticated:
        context['user_preferences'] = UserPreferences.objects.filter(
            user=request.user
        ).first()
    return context



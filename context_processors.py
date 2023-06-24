from .models import Thread

def get_unread_messages_count(request):
    if request.user.is_authenticated:
        chat_count = 0
        obj = Thread.objects.by_user(request.user)
        for i in obj:
            chat_count += i.chatmessage_set.filter(read=False).count()
    else:
        chat_count = None
    return {
        'chat_count': chat_count,
    }
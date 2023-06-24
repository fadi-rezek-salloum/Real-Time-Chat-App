import os
import random
import string

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils.text import Truncator


def upload_file_to(instance, filename):
    length = 13
    chars = string.ascii_letters + string.digits
    random.seed = (os.urandom(1024))
    random_name = ''.join(random.choice(chars) for i in range(length))

    file_name = f"{random_name}.{filename.split('.')[-1]}"

    return f"chat/{file_name}"


class ThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def get_or_new(self, user, other_id):
        id = user.id
        if id == other_id:
            return None
        qlookup1 = Q(first__id=id) & Q(second__id=other_id)
        qlookup2 = Q(first__id=other_id) & Q(second__id=id)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            Klass = user.__class__
            user2 = Klass.objects.get(id=other_id)
            if user != user2:
                obj = self.model(
                        first=user, 
                        second=user2
                    )
                obj.save()
                return obj, True
            return None, False


class Thread(models.Model):
    first = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_thread_first')
    second = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_thread_second')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    objects = ThreadManager()

    @property
    def room_group_name(self):
        return f'chat_{self.id}'


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='sender', on_delete=models.CASCADE)

    message = models.TextField(null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to=upload_file_to)

    timestamp = models.DateTimeField(auto_now_add=True)

    read = models.BooleanField(default=False)

    def __str__(self):
        if self.message:
            return Truncator(str(self.message)).chars(50, html=True)
        else:
            return str(_('تم إرسال ملف'))
    
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None
    
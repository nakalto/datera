from .models import Thread
def normalize(u1, u2):
    return (u2, u1) if u1.id > u2.id else (u1, u2)
def get_or_create_thread(u1, u2):
    u1,u2 = normalize(u1,u2)
    obj,_ = Thread.objects.get_or_create(a=u1, b=u2)
    return obj
def can_send(user, thread, entitled: bool):
    flag = "a_first_free_used" if thread.a_id == user.id else "b_first_free_used"
    if not getattr(thread, flag): return True
    return entitled

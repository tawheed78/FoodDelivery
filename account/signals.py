from django.db.models.signals import post_save
from django.dispatch import receiver
from . models import User, UserProfile

 
@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender,instance,created,**kwargs):
    print(created)
    if created:
        UserProfile.objects.create(user=instance)

    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            #create the user profile if not exists
            UserProfile.objects.create(user=instance)


# post_save.connect(post_save_create_profile_receiver, sender=User)
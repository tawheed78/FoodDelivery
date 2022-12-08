from django.db import models
from account.models import User, UserProfile
from account.utils import send_notification

# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name
        
    def save(self, *args, **kwargs):
        if self.pk is not None:
            #update
            original_status = Vendor.objects.get(pk=self.pk) 
            if original_status.is_approved != self.is_approved:
                mail_template = 'account/emails/admin_approval_email.html'
                context = {
                        'user' : self.user,
                        'is_approved' : self.is_approved
                    }
                if self.is_approved == True:
                    #send noti.
                    mail_subject = 'Congratulations. You are approved'
                    send_notification(mail_subject, mail_template, context)
                   
                else:
                    #send noti
                    mail_subject = 'We are extremely sorry, but you are not eligible to publish on our domain.Thankyou.'
                    send_notification(mail_subject, mail_template, context)

        return super(Vendor, self).save(*args, **kwargs) #super fn will allow too access the save method of ths class
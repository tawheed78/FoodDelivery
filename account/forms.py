from django import forms
from . models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phonenumber', 'password']
    
    def clean(self):                                     #django model form by default calls the clean method behind 
        cleaned_data = super(UserForm,self).clean()      #the scene whenever the form is triggered. The super fn gives the ability to oveerride the clean method ehich is inbuilt
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password') 

        if password != confirm_password:
            raise forms.ValidationError(
                'Password does not match'
            )
                                                         
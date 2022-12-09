import os
from django.core.exceptions import ValidationError

def image_validator(value):
    ext = os.path.splitext(value.name)[1]
    print(ext)
    valid_extensions = ['png','jpg','jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported extension.Valid extensions:"+str(valid_extensions))
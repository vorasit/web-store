from django.contrib.auth.models import User

admin = User.objects.get(username='admin')
admin.set_password('admin1234')
admin.save()

print('Admin password has been set successfully.')

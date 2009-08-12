from django.core.management import setup_environ

from django.core import management

print "Setting up Django environment."

from tdsurface import settings

setup_environ(settings)

from tdsurface.depth.models import Settings, Well

management.call_command('flush', verbosity=0, interactive=False)

management.call_command('loaddata', 'test_well.json', verbosity=5)

print Well.objects.all()

active_well, created = Settings.objects.get_or_create(name='ACTIVE_WELL')

print Well.objects.get(pk=active_well.value)

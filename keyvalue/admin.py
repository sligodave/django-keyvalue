
from django.contrib import admin

from keyvalue.models import Key, KeyValue, ValueBoolean, ValueInteger,\
                            ValueText, ValueChar100, ValueChar50

admin.site.register(Key)
admin.site.register(KeyValue)
admin.site.register(ValueBoolean)
admin.site.register(ValueInteger)
admin.site.register(ValueText)
admin.site.register(ValueChar100)
admin.site.register(ValueChar50)

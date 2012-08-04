from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import post_delete
from django.dispatch import receiver

from keyvalue.managers import KeyValueManager

"""
Each keyvalue has three items.
1. An owner which must be an instance of a django model
2. A key, which must be an instance of keyvalue.models.Key
3. A value, which must be one of:
    - an instance of a django model
    - a field on an instance of a django model
    - a bool
    - an integer
    - a string

   Note: When a bool, integer or string is supplied as a value
   we store it in supplied keyvalue value django model.
   But to the user it appears as it's original format.
   You can set what type of container we just for storing the string values.
   Supplied containers are: ValueText, ValueChar100, ValueChar50
"""


class Key(models.Model):
    """
    This is mainly a co-ordinater for instances of KeyValue
    which have the same name.
    It contains meta information for a KeyValue name, that
    we don't need to repeat for each instance of the KeyValue

    name = The name of the keys that will user this master.
    verbose_name = The human printable version of the name.
    description = A longer description of the key.
    """
    name = models.CharField(max_length=50,
                            help_text="Name of the KeyValue",
                            unique=True)
    verbose_name = models.CharField(max_length=100, null=True, blank=True,
                                    help_text="Human readable "\
                                    "version of the name")
    description = models.CharField(max_length=150, null=True, blank=True,
                                   help_text="Description of what "\
                                   "this key represents")

    def __unicode__(self):
        if not self.description:
            return self.name
        return u'%s - %s' % (self.name, self.description)

    def save(self, *args, **kwargs):
        if self.verbose_name == None:
            verbose_name = self.name.title()
            verbose_name = verbose_name.replace('-', ' ')
            verbose_name = verbose_name.replace('_', ' ')
            self.verbose_name = verbose_name.replace('.', ' ')
        super(Key, self).save(*args, **kwargs)


class KeyValue(models.Model):
    """
    Hangs a key and a value off any instance of any django model.
    """
    objects = KeyValueManager()

    # Key instance that specifies the characteristics of the keyvalue key
    key = models.ForeignKey(Key)

    # Model instance that is the owner of this key
    owner_content_type = models.ForeignKey(ContentType,
                                           related_name="keyvalue_owners")
    owner_object_id = models.PositiveIntegerField()
    owner_content_object = generic.GenericForeignKey('owner_content_type',
                                                     'owner_object_id')

    # Model instance that is the value of this key
    value_content_type = models.ForeignKey(ContentType,
                                           related_name="keyvaule_values")
    value_object_id = models.PositiveIntegerField()
    value_content_object = generic.GenericForeignKey('value_content_type',
                                                     'value_object_id')
    # Should investigate a correct max_length for this
    value_content_object_field = models.CharField(max_length=100,
                                                  null=True, blank=True)

    # Should we delete the value of this Keyvalue instance on delete.
    cascade_on_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('key', 'owner_content_type', 'owner_object_id')

    @property
    def name(self):
        return self.key.name

    @property
    def verbose_name(self):
        return self.key.verbose_name

    @property
    def description(self):
        return self.key.description

    @property
    def value(self):
        # Is the value a field on a model instance
        if self.value_content_object_field and\
            hasattr(self.value_content_object,
                    self.value_content_object_field):
            return getattr(self.value_content_object,
                           self.value_content_object_field)
        # Or a model instance.
        return self.value_content_object

    @property
    def owner(self):
        return self.owner_content_object

    def __unicode__(self):
        res = u'%s = %s.%s' % (self.key.name,
                              self.value_content_type.app_label,
                              self.value_content_type.model)
        if self.value_content_object_field:
            res += u'.%s' % self.value_content_object_field
        res += u' (%s)' % self.value
        return res


@receiver(post_delete, sender=KeyValue)
def keyvalue_delete_handler(sender, instance, **kwargs):
    """
    When a keyvalue is deleted we can also delete the value of the keyvalue.
    We don't by default but if the keyvalue says to
    then we will delete the value object when the key is deleted.
    NOTE: If we are cascading the delete, we will delete the whole model
    instance not just the field on a model instance if one was specified.
    """
    if instance.cascade_on_delete == True:
        instance.value_content_object.delete()


#
# If we are passed a value that is not a django Model
# The other value types we support are Boolean, Integer,
# Text and a 50 or 100 length Char.
# They are all stored in their corrisponding django model fields.
#


class ValueBase(models.Model):
    """
    Container Model for when we are saving a keyvalue who's value is
    a boolean, integer or string.
    """
    keyvalues = generic.GenericRelation(KeyValue,
                                    content_type_field='value_content_type',
                                    object_id_field='value_object_id')

    class Meta:
        abstract = True

    def __unicode__(self):
        if self.keyvalues.all():
            keyvalue = self.keyvalues.all()[0]
            return keyvalue.__unicode__()
        return u'%s' % self.value


class ValueBoolean(ValueBase):
    value = models.BooleanField()


class ValueInteger(ValueBase):
    value = models.IntegerField()


class ValueText(ValueBase):
    value = models.TextField()


class ValueChar100(ValueBase):
    value = models.CharField(max_length=100)


class ValueChar50(ValueBase):
    value = models.TextField(max_length=50)

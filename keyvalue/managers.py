from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class KeyValueManager(models.Manager):
    def __dynamic_key(self, name):
        """
        If the setting to create Key instances that don't exist is set to True,
        then we create a Key instance when one doesn't exist.
        """
        if getattr(settings, 'KEYVALUE_DYNAMIC_KEYS', True):
            from keyvalue.models import Key
            Key.objects.get_or_create(name=name)

    def has_keyvalue(self, owner, name):
        """
        Test if a given owner has an instance of
        keyvalue with the name provided
        """
        return self.has_keyvalues(owner, [name])

    def has_keyvalues(self, owner, names):
        """
        Test if a given owner has an instance of
        keyvalue for all the names provided
        """
        qs = self.get_query_set()
        owner_type = ContentType.objects.get_for_model(owner)
        return len(names) == qs.filter(owner_content_type=owner_type,
                                       owner_object_id=owner.id,
                                       key__name__in=names).count()

    def get_keyvalue(self, owner, name):
        """
        Get a keyvalue instance for a given owner and a given name
        """
        keyvalues = self.get_keyvalues(owner, [name])
        if not keyvalues:
            raise self.model.DoesNotExist()
        return keyvalues[0]

    def get_keyvalues(self, owner, names=None):
        """
        Delete a keyvalue instance for a given owner
        """
        owner_type = ContentType.objects.get_for_model(owner)
        filter_args = {'owner_content_type': owner_type,
                       'owner_object_id': owner.id}
        if not names == None:
            filter_args['key__name__in'] = names
        return self.get_query_set().filter(**filter_args)

    def set_keyvalue(self, owner, name, value,
                     field=None, cascade_on_delete=None):
        from keyvalue.models import Key, ValueBoolean, ValueInteger
        if isinstance(value, (bool, int, basestring)):
            if isinstance(value, bool):
                value = ValueBoolean.objects.create(value=value)
            if isinstance(value, int):
                value = ValueInteger.objects.create(value=value)
            if isinstance(value, basestring):
                cls_path = getattr(settings, 'KEYVALUE_TEXT_VALUE_TYPE',
                                  'keyvalue.models.ValueText')
                path, cls = cls_path.rsplit('.', 1)
                mod = __import__(path, fromlist=[cls])
                Cls = getattr(mod, cls)
                value = Cls.objects.create(value=value)
            field = 'value'
            # Unless we are told otherwise, we'll delete the values
            # instances on delete of the key, because we created it
            # purely for storage of a bool, int or string
            if cascade_on_delete == None:
                cascade_on_delete = True
        self.__dynamic_key(name)
        kwargs = {
            'key': Key.objects.get(name=name),
            'owner_content_type': ContentType.objects.get_for_model(owner),
            'owner_object_id': owner.id,
            'value_content_type': ContentType.objects.get_for_model(value),
            'value_object_id': value.id,
        }
        if not field == None:
            kwargs['value_content_object_field'] = field
        if not cascade_on_delete == None:
            kwargs['cascade_on_delete'] = cascade_on_delete
        # return self.get_query_set().get_or_create(**kwargs)[1]
        return self.get_or_create(**kwargs)[0]

    def set_keyvalues(self, owner, keyvalues,
                      fields={}, cascade_on_deletes={}):
        results = []
        for name, value in keyvalues.items():
            results.append(self.set_keyvalue(owner, name, value,
                                        fields.get(name, None),
                                        cascade_on_deletes.get(name, None)))
        return results

    def del_keyvalue(self, owner, name):
        """
        Delete a keyvalue instance for a given owner
        """
        self.del_keyvalues(owner, [name])

    def del_keyvalues(self, owner, names=None):
        """
        Delete a list of keyvalue instances for a given user.
        """
        if names == None:
            names = self.get_keyvalues(owner).values_list('key__name',
                                                          flat=True)
        owner_type = ContentType.objects.get_for_model(owner)
        qs = self.get_query_set()
        qs.filter(owner_content_type=owner_type,
                  owner_object_id=owner.id,
                  key__name__in=names).delete()


from django.test import TestCase
from django.test.utils import override_settings

from keyvalue.models import Key, KeyValue, ValueChar50


KEYVALUE_TEST_SETTINGS = {
                    'KEYVALUE_TEXT_VALUE_TYPE': 'keyvalue.models.ValueText',
                    'KEYVALUE_DYNAMIC_KEYS': True
}


@override_settings(**KEYVALUE_TEST_SETTINGS)
class KeyTest(TestCase):
    def setUp(self):
        # We need a Model instance as an owner,
        # we can't rely on any other Model existing, like User or Site
        # We will use this instance as the owner for the keyvalues we'll
        # be setting.
        self.owner = Key.objects.create(name="Owner")

        # Create 4 Key instances
        self.key1 = Key.objects.create(name="K1")
        self.key2 = Key.objects.create(name="K2", description="Key 2")
        self.key3 = Key.objects.create(name="K3", description="Key 3")
        self.key4 = Key.objects.create(name="K4", description="Key 4")

        # Create 1 KeyValue instance
        self.keyvalue = KeyValue.objects.set_keyvalue(owner=self.owner,
                                                       name='K1', value='Yo')
        # Create 3 KeyValue Instances
        self.keyvalues = KeyValue.objects.set_keyvalues(owner=self.owner,
                                                        keyvalues={'K2': 10,
                                                        'K3': 'Hello',
                                                        'K4': True})
        # Create 1 KeyValue Instance, also dynamically creates a Key
        self.keyvalue2 = KeyValue.objects.set_keyvalue(owner=self.owner,
                                                       name='K5',
                                                       value=self.owner)
        # We start each test with 6 Keys (including Owner) and 5 KeyValues
        # They all belong to the Key model instance 'Owner' with an id of 1
        # It's just used because we know it exists but it could be any
        # django model instance.

    def test_key(self):
        # Make sure all 5 keys were created
        self.assertEqual(Key.objects.all().count(), 6)
        # Do a quick match on the first Key created
        self.assertEqual(self.key1, Key.objects.get(id=2))
        # Test name field on Key
        self.assertEqual(self.key1.name, 'K1')
        # Test __unicode__ method on Key without description
        self.assertEqual(str(self.key1), 'K1')
        # Test __unicode__ method on Key with description
        self.assertEqual(str(self.key2), 'K2 - Key 2')

    def test_keyvalue(self):
        self.assertEqual(self.keyvalue.name, 'K1')
        self.assertEqual(self.keyvalue.verbose_name, 'K1')
        self.assertEqual(self.keyvalue.description, None)
        self.assertEqual(self.keyvalue.value, 'Yo')
        self.assertEqual(self.keyvalue.owner, self.owner)
        self.assertEqual(self.keyvalue2.value, self.owner)
        self.assertEqual(KeyValue.objects.all().count(), 5)
        KeyValue.objects.del_keyvalue(self.owner, 'K1')
        self.assertEqual(KeyValue.objects.all().count(), 4)
        self.assertEqual(KeyValue.objects.get_keyvalue(self.owner,
                                                       'K2').value, 10)
        self.assertEqual(KeyValue.objects.has_keyvalue(self.owner, 'K4'), True)
        KeyValue.objects.del_keyvalues(self.owner)
        self.assertEqual(KeyValue.objects.has_keyvalue(self.owner, 'K4'),
                         False)
        self.assertEqual(KeyValue.objects.all().count(), 0)
        # Ensure error when key doesn't exist
        # and KEYVALUE_DYNAMIC_KEYS is False
        with self.settings(KEYVALUE_DYNAMIC_KEYS=False):
            self.assertRaises(Key.DoesNotExist, KeyValue.objects.set_keyvalue,
            *[self.owner, 'NO_KEY_OF_THIS_NAME', 6])

    def test_value(self):
        self.assertEqual(self.keyvalue.value, 'Yo')
        self.assertEqual(str(self.keyvalue.value_content_object),
                         'K1 = keyvalue.valuetext.value (Yo)')
        with self.settings(
                        KEYVALUE_TEXT_VALUE_TYPE='keyvalue.models.ValueChar50',
                        KEYVALUE_DYNAMIC_KEYS=True):
            KeyValue.objects.set_keyvalue(self.owner, 'K6', 'H',
                                          cascade_on_delete=False)
        self.assertEqual(ValueChar50.objects.all().count(), 1)
        KeyValue.objects.del_keyvalues(self.owner)
        self.assertEqual(KeyValue.objects.all().count(), 0)
        self.assertEqual(ValueChar50.objects.all().count(), 1)
        self.assertEqual(str(ValueChar50.objects.all()[0]), 'H')

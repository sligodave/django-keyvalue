django-keyvalue
===============

``django-keyvalue`` is a straight forward key value store for hanging off Django Model instances.

Give the ability to hang any name value pair off of any instance of a Django Model.

The KeyValue model holds a reference to the Owner (an instance of a django model) and a value,
which is also an instance of a django model but you have the ability to specify a field on the model as the value also.

Each KeyValue has three items:
- An owner which must be an instance of a django model
- A key, which must be an instance of keyvalue.models.Key and stores the name of the key part of the key value.
- A value, which must be one of:
  - an instance of a django model
  - a field on an instance of a django model
  - a bool
  - an integer
  - a string

```
   Note: When a bool, integer or string is supplied as a value
   we store it in supplied keyvalue value django model.
   But to the user it appears as it's original format.
   You can set what type of container is used for storing the string values.
   Supplied containers are: ValueText, ValueChar100, ValueChar50
```

NOTE: This application is still being worked on.
Speed wise you are always better explicitly specifying your fields and relationships on your models using django fields.
I can see a use for this though where you want your models to organically grown and the relationships between them.


## LIMITATIONS:

1. This app uses djangos generic replationships, as such I made a decision to stick with Models who's ID's are positive integers.
This means that you can only use Models with positive integers as their IDs for the Owner of the KeyValue and also the Value of the KeyValue instance.
2. If the value to a KeyValue instance points to a field of a model, rather than a model itself.
The length of the field name must currently be less than 100 characters. This may be revised at a later date.

Also, there are better docs to follow.
See TODO.txt for a general direction.


## INSTALL:

Clone this repository into your Sublime Text *Packages* directory.

    git clone https://github.com/sligodave/django-keyvalue.git django-keyvalue
    
    python setup.py
    
    Add "keyvalue" to your INSTALLED_APPS and syncdb and you are ready to go.


## EXAMPLE:

    >>> from django.contrib.auth.models import User
    >>> from your_app.models import YourModel
    >>> from keyvalue.models import KeyValue
    >>> 
    >>> u = User.objects.get(username="bob")
    >>> ym = YourModel.objects.get(id=5)
    >>> 
    >>> KeyValue.objects.set_keyvalue(owner=ym, name='name', value='Bob')
    >>> KeyValue.objects.set_keyvalue(ym, 'email', 'bob@example.com')
    >>> KeyValue.objects.set_keyvalue(ym, 'user', u)
    >>> KeyValue.objects.set_keyvalue(owner=ym, name='username', value=u, field='username')
    >>> 
    >>> KeyValue.objects.get_keyvalue(ym, 'username').value
    u'bob'
    >>> KeyValue.objects.get_keyvalue(ym, 'user').value
    <User: bob>

For more examples see the unit tests in the keyvalue directory.


## Todo:

(In no specific order)

- Increase amount of unittests.
- Use correct comment structure to create sphinx documents.
- Improve documentation and guides.
- Admin helper
- Create example project
- Templatetags
- Insert a cascade_on_delete to the Key model also, to specify for all instances of Keyvalue, rather than setting it on an instance by instance basis.
- Investigate proper limit on the "value_content_object_field" field on Keyvalue. It should be set to the max length that a Model Fields name can be.
- Should the limit of one instance of any Key per owner be optional, set on a per Key basis?
- Possible API?
- Improve exception handling in utility methods on KeyValue Manager


## Issues and suggestions:

Fire on any issues or suggestions you have.


## Copyright and license
Copyright 2013 David Higgins

[MIT License](LICENSE)

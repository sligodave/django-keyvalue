django-keyvalue
===============

``django-keyvalue`` is a straight forward key value store for hanging off Django Model instances.

Give the ability to hang any name value pair off of any instance of a Django Model.

The KeyValue model holds a reference to the Owner (an instance of a django model) and a value,
which is also an instance of a django model but you have the ability to specify a field on the model as the value also.

Each KeyValue has three items:
1. An owner which must be an instance of a django model
2. A key, which must be an instance of keyvalue.models.Key and stores the name of the key part of the key value.
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

NOTE: This application is still being worked on.
Speed wise you are always better explicitly specifying your fields and relationships on your models using django fields.
I can see a use for this though where you want your models to organically grown and the relationships between them.

Also, there are better docs to follow.
See TODO.txt for a general direction.

INSTALL:
Add "keyvalue" to your INSTALLED_APPS and syncdb and you are ready to go.

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

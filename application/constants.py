# -*- coding: utf-8 -*-

import os
from collections import OrderedDict
from flask import Markup


INACTIVE = 0
NEW = 1
ACTIVE = 2
USER_STATUS = {
    INACTIVE: 'inactive',
    NEW: 'new',
    ACTIVE: 'active',
}
USER_STATUS = OrderedDict(sorted(USER_STATUS.items()))

DEFAULT_USER_AVATAR = 'default.jpg'

SEX_TYPES = {
    1: 'Male',
    2: 'Female',
    3: 'Other',
}
SEX_TYPES = OrderedDict(sorted(SEX_TYPES.items()))

INSTANCE_FOLDER_PATH = os.path.join('/tmp', 'instance')

ALLOWED_AVATAR_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

AGREE_TIP = Markup(
    'Agree to the <a target="blank" href="/terms">Terms of Service</a>')

BIO_TIP = "Tell us about yourself"

STRING_LEN = 225

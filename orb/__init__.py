"""
ORB stands for Object Relation Builder and is a powerful yet simple to use \
database class generator.
"""

# define authorship information
__authors__ = ['Eric Hulser']
__author__ = ','.join(__authors__)
__credits__ = []
__copyright__ = 'Copyright (c) 2011, Projex Software'
__license__ = 'LGPL'

# maintenance information
__maintainer__ = 'Eric Hulser'
__email__ = 'eric.hulser@gmail.com'

# auto-generated version file from releasing
try:
    from ._version import __major__, __minor__, __revision__, __hash__
except ImportError:
    __major__ = 0
    __minor__ = 0
    __revision__ = 0
    __hash__ = ''

__version_info__ = (__major__, __minor__, __revision__)
__version__ = '{0}.{1}.{2}'.format(*__version_info__)


import logging
logger = logging.getLogger(__name__)

# import global symbols
from . import errors
from .decorators import *

from .core import events
from .core.column import Column
from .core.collection import Collection
from .core.connection import Connection
from .core.context import Context
from .core.database import Database
from .core.index import Index
from .core.model import Model
from .core.modelmixin import ModelMixin
from .core.query import (Query, QueryCompound)
from .core.pipe import Pipe
from .core.schema import Schema
from .core.syntax import Syntax
from .core.security import Security
from .core.system import System

from .core.model_types import *
from .core.column_types import *
from .core.connection_types import *
from .core.syntax_types import *

# define the global system
system = System()
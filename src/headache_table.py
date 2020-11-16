import sys
sys.path.insert(0, "../utils/database")
from database import *

class HeadacheTable(DBTable):
    def __init__(self):
        self.TABLE_NAME  = "HEADACHE"
        fields = [\
            DBField("ENTRY",    "INTEGER", True),
            DBField("TIME",     "INTEGER", False),
            DBField("HEADACHE", "INTEGER", False),
        ]
        parent=super(HeadacheTable, self)
        parent.__init__(self.TABLE_NAME, fields)

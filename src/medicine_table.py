import sys
sys.path.insert(0, "../utils/database")
from database import *

class MedicineTable(DBTable):
    def __init__(self):
        self.TABLE_NAME  = "MEDICINE"
        fields = [\
            DBField("ENTRY",    "INTEGER", True),
            DBField("TIME",     "INTEGER", False),
            DBField("MEDICINE", "TEXT", False),
        ]
        parent=super(MedicineTable, self)
        parent.__init__(self.TABLE_NAME, fields)

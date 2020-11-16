import sys
sys.path.insert(0, "../utils/database")
from database import *

class MasterTable(DBTable):
    def __init__(self):
        self.TABLE_NAME  = "MEDICINE"
        fields = [\
            DBField("ENTRY",    "INTEGER", True),
            DBField("TIME",     "INTEGER", False),
            DBField("MEDICINE", "TEXT",    False),
            DBField("HEADACHE", "INT",     False),
        ]
        parent=super(MasterTable, self)
        parent.__init__(self.TABLE_NAME, fields)
    def add_entry(self, conn, entry, time, med=None, well=None):
        add_tuple = (entry, time, med, well)
        super(MasterTable, self).add_entry(conn, add_tuple)

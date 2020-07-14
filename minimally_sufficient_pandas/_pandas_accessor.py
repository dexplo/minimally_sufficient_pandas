import re

import pandas as pd


@pd.api.extensions.register_dataframe_accessor("msp")
class _MSP:

    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self.select = Select()

    def reset_index(self):
        pass




class Select:

    def __getitem__(self, item):
        pass

doc = pd.DataFrame.reset_index.__doc__
_MSP.reset_index.__doc__ = re.sub('df : .*(?=filename :)', '',  doc, flags=re.S)

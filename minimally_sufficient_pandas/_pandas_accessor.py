import re
from functools import wraps

import pandas as pd
from IPython.display import display


@pd.api.extensions.register_dataframe_accessor("msp")
class _MSP:

    def __init__(self, df):
        self._df = df
        self.select = Select(df)
        self.op = Op(df)
        self.to = To(df)
        same_methods = ['isna', 'copy', 'head', 'tail', 'isin', 'where', 'query', 
                        'agg', 'groupby', 'rolling', 'abs', 'all', 'any', 'clip', 'round',
                        'quantile', 'diff', 'drop', 'drop_duplicates', 'interpolate',
                        'dropna', 'replace', 'pivot_table', 'nlargest', 'nsmallest',
                        'melt', 'T', 'append', 'merge', 'asfreq', 'resample', 'plot',
                        'asfreq', 'idxmax', 'idxmin']
        for method in same_methods:
            old_method = getattr(self._df, method)
            setattr(self, method, old_method)
       
    @property
    def index(self):
        return self._df.index

    @property
    def values(self):
        return self._df.values

    @property
    def shape(self):
        return self._df.shape

    @property
    def dtypes(self):
        return self._df.dtypes
    
    def flatten_index(self, axis='index', sep='_', inplace=False):
        """
        Flatten MultiLevel Index to a single level

        Parameters
        ----------
        axis : 'index', 'columns', or 'both', default 'index'
            Flatten just the index, the columns, or both

        sep : str, deault '_'
            Character(s) to separate index level values with

        inplace : bool, default False
            Mutate DataFrame in place when True, otherwise make a copy
        """
        if axis not in ('index', 'columns', 'both'):
            raise ValueError("axis must be 'index', 'columns', or 'both'")
        df = self._df
        if not inplace:
            df = df.copy()

        def flatten(cur_axis):
            idx = getattr(df, cur_axis)
            if isinstance(idx, pd.MultiIndex):
                new_idx = idx.get_level_values(0).astype('str')
                for i in range(1, idx.nlevels):
                    new_idx += sep + idx.get_level_values(i)
                setattr(df, cur_axis, new_idx)

        if axis == 'index' or axis == 'both':
            flatten('index')
        if axis == 'columns' or axis == 'both':
            flatten('columns')

        if not inplace:
            return df

    ### Aggregation methods
        
    def max(self, axis=None, skipna=None, level=None, numeric_only=None, keep_df=True):
        return self._agg('max', axis=axis, skipna=skipna, level=level, 
                         numeric_only=numeric_only, keep_df=keep_df)
        
    def min(self, axis=None, skipna=None, level=None, numeric_only=None, keep_df=True):
        return self._agg('min', axis=axis, skipna=skipna, level=level, 
                         numeric_only=numeric_only, keep_df=keep_df)

    def mean(self, axis=None, skipna=None, level=None, numeric_only=None, keep_df=True):
        return self._agg('mean', axis=axis, skipna=skipna, level=level, 
                         numeric_only=numeric_only, keep_df=keep_df)

    def median(self, axis=None, skipna=None, level=None, numeric_only=None, keep_df=True):
        return self._agg('median', axis=axis, skipna=skipna, level=level, 
                         numeric_only=numeric_only, keep_df=keep_df)

    def sum(self, axis=None, skipna=None, level=None, numeric_only=None, min_count=0, keep_df=True):
        return self._agg('sum', axis=axis, skipna=skipna, level=level, 
                         numeric_only=numeric_only, min_count=min_count, keep_df=keep_df)

    def std(self, axis=None, skipna=None, level=None, ddof=1, numeric_only=None, keep_df=True):
        return self._agg('std', axis=axis, skipna=skipna, level=level, ddof=ddof, 
                         numeric_only=numeric_only, keep_df=keep_df)

    def var(self, axis=None, skipna=None, level=None, ddof=1, numeric_only=None, keep_df=True):
        return self._agg('var', axis=axis, skipna=skipna, level=level, ddof=ddof, 
                         numeric_only=numeric_only, keep_df=keep_df)

    def count(self, axis=None, level=None, numeric_only=None, keep_df=True):
        return self._agg('count', axis=axis, level=level, 
                          numeric_only=numeric_only, keep_df=keep_df)

    def nunique(self, axis=0, dropna=True, keep_df=True):
        return self._agg('nunique', axis=axis, dropna=dropna, keep_df=keep_df)

    def mode(self, axis=0, numeric_only=False, dropna=True):
        return self._df.mode(axis=axis, numeric_only=numeric_only, dropna=dropna)

    def _agg(self, method_name, **kwargs):
        keep_df = kwargs.pop('keep_df')
        obj = getattr(self._df, method_name)(**kwargs)
        if keep_df and isinstance(obj, pd.Series):
            df = obj.to_frame(method_name)
            if kwargs['axis'] in [None, 0, 'rows', 'index']:
                df = df.T
        else:
            df = obj
        return df

    def display(self, top=100, bottom=0, max_columns=None):
        """
        Display the top/bottom n rows of the DataFrame. This only displays the 
        DataFrame visually in the output and does NOT return it. None is 
        always returned. Use the head/tail methods to return a DataFrame

        Parameters
        ----------
        top : int, default 100
            Number of rows to display from the top of the DataFrame.
            When <=0, no DataFrame is displayed

        bottom : int, default 0
            Number of rows to display from the bottom of the DataFrame.
            When <=0, no DataFrame is displayed

        max_columns : int, default None
            Controls the pd.options.display.max_columns property. 
            When None (default), all column get displayed.

        Returns
        -------
        None
        """
        with pd.option_context('display.max_rows', None, 'display.max_columns', max_columns):
            if top > 0:
                display(self._df.head(top).style.set_caption(f'Top {top} rows'))
            if bottom > 0:
                display(self._df.tail(bottom).style.set_caption(f'Bottom {bottom} rows'))    

    def reset_index(self, level=None, drop=False, inplace=False, col_level=0, 
                    col_fill='', names=None):
        """
        names : str or list of str, default None
            Rename the index level(s) of the DataFrame before resetting 
            the index. These name(s) will become the new column names.
        """
        df = self._df
        if names:
            df = self._df.rename_axis(names)
        return df.reset_index(level, drop, inplace, col_level, col_fill)

    def rename(index=None, columns=None, copy=True, inplace=False):
        return self._df.rename(index=index, columns=columns, copy=copy, inplace=inplace)


class Select:

    def __init__(self, df):
        self._df = df

    def __getitem__(self, item):
        return self._df.loc[item]


class Op:

    def __init__(self, df):
        self._df = df
        methods = ['add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'pow', 'dot', 
                   'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv', 'rfloordiv', 'rmod', 'rpow', 
                   'lt', 'gt', 'le', 'ge', 'ne', 'eq']

        for method in methods:
            old_method = getattr(self._df, method)
            setattr(self, method, old_method)


class To:

    def __init__(self, df):
        self._df = df
        methods = ['parquet', 'pickle', 'csv', 'hdf', 'sql', 'dict', 'excel', 
                   'json', 'html', 'feather', 'latex', 'stata', 'gbq', 'records', 
                   'string', 'clipboard', 'markdown']

        for method in methods:
            old_method = getattr(self._df, 'to_' + method)
            setattr(self, method, old_method)


_agg_methods = ['max', 'min', 'mean', 'median', 'sum', 'std', 'var',
                'count', 'nunique', 'mode']
_keep_df_doc = """
                keep_df : bool, default True
                    When True, returns the result as a DataFrame, keeping the 
                    original dimension of the non-aggregating axis.
                """

for method in dir(_MSP):
    if method.startswith('_'):
        continue
    pd_method = getattr(pd.DataFrame, method, None)
    if pd_method is not None:
        pd_doc = getattr(pd_method, '__doc__')
        msp_method = getattr(_MSP, method)
        if method in _agg_methods:
            msp_doc = _keep_df_doc
        else:
            msp_doc = getattr(msp_method, '__doc__') or ''

        msp_doc = [line.strip() for line in msp_doc.split('\n')[1:-1]]
        msp_doc = '\n    '.join(msp_doc) + '\n\n'
        new_msp_doc = re.sub('(?=Returns\n---)', msp_doc,  pd_doc)
        setattr(msp_method, '__doc__', new_msp_doc)

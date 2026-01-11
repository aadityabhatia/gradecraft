import polars as pl
import os

# this allows categorical data from various sources to be combined and handled gracefully; performance cost is acceptable
pl.enable_string_cache()


class DataModel:
    df = None
    dbTable = None
    filename = None
    schema = None
    dataset = None
    table = None

    def __init__(self, dataset, table=None, dataPath=None, schema=None, df=None):

        dataPath = dataPath or os.getenv("DATA_PATH")
        self.dataset = dataset
        self.table = table = self.table or table or self.__class__.__name__.lower()
        self.dbTable = f"{dataset}-{table}".replace('.', '-')

        if schema is not None:
            self.schema = schema

        if df is not None:
            if not isinstance(df, pl.DataFrame):
                df = pl.from_pandas(df)
            self.df = df

            if self.schema is None:
                self.schema = df.schema
            else:
                self.df = self.df.cast(self.schema)

        if dataPath is not None:
            self.filename = f'{dataPath}/{dataset}/{table}.parquet'
            os.makedirs(f'{dataPath}/{dataset}', exist_ok=True)

    def initialize(self):
        if self.df is None and self.schema is not None:
            self.df = pl.DataFrame(schema=self.schema)
        return self

    def preprocess(self, lazyFrame: pl.LazyFrame) -> pl.LazyFrame:
        """Override this method to preprocess the dataframe after loading from CSV"""
        return lazyFrame

    def save(self):
        self.df.write_parquet(self.filename)
        return self

    def load_from_parquet(self, **kwargs):
        self.df = pl.read_parquet(self.filename, **kwargs)
        if self.schema is None:
            self.schema = self.df.schema
        else:
            self.df = self.df.cast(self.schema)
        return self

    def exists(self):
        return os.path.exists(self.filename)

    def save_to_parquet(self, **kwargs):
        self.df.write_parquet(self.filename, **kwargs)
        return self

    def addRow(self, row_dict):
        """Add a row to the dataframe. The row_dict must have the same keys as the schema."""
        df_new = pl.DataFrame(row_dict, schema=self.schema)
        self.df.vstack(df_new, in_place=True)

    def addColumns(self, *args, **kwargs):
        """Add a column to the dataframe"""
        self.df = self.df.with_columns(*args, **kwargs)
        self.schema = self.df.schema

    def join(self, df_new, on, how='left'):
        """Shorthand to left join with another dataframe on specified column"""
        return self.df.join(df_new, on=on, how=how)

    def join_in_place(self, df_new, on, dropColumns=None):
        """Shorthand to left join with another dataframe on specified column"""
        if dropColumns is not None:
            self.df = self.df.drop(dropColumns)
        self.df = self.join(df_new, on=on, how='left')
        return self

    def get(self, **kwargs):
        """Shorthand for df.filter()"""
        predicate = None
        for key, value in kwargs.items():
            if predicate is None:
                predicate = pl.col(key) == value
            else:
                predicate = predicate & (pl.col(key) == value)
        return self.df.filter(predicate)

    def glimpse(self, **kwargs):
        """shorthand for df.glimpse()"""
        return self.df.glimpse(**kwargs)


class Problems(DataModel):
    schema = {
        'problemId': pl.UInt16,
        'name': pl.String,
        'description': pl.String,
        'points': pl.Float32,
        'dueDate': pl.Int64,
    }


class Submissions(DataModel):
    schema = {
        'studentId': pl.UInt32,
        'problemId': pl.UInt16,
        'filename': pl.String,
        'submission': pl.String,
        'submittedAt': pl.Datetime,
        'late': pl.Boolean,
    }


class Criteria(DataModel):
    schema = {
        'problemId': pl.UInt16,
        'criteriaId': pl.UInt16,
        'summary': pl.String,
        'details': pl.String,
        'minScore': pl.Int8,
        'maxScore': pl.Int8,
    }


class Evaluations(DataModel):
    schema = {
        'studentId': pl.UInt32,
        'studentName': pl.String,
        'section': pl.String,
        'studentResponse': pl.String,
        'problemId': pl.UInt16,
        'gradedAt': pl.Datetime,
        'modelName': pl.String,
        'scores': pl.List(pl.Int8),
        'reasons': pl.List(pl.String),
        'comments': pl.List(pl.String),
    }


class Students(DataModel):
    schema = {
        'canvasId': pl.UInt32,
        'zyUserId': pl.UInt32,
        'section': pl.Categorical,
        'name': pl.String,
        'firstName': pl.String,
        'lastName': pl.String,
        'email': pl.String,
    }

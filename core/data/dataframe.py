import pandas
import numpy as np
from sklearn.model_selection import train_test_split


class Dataloader(object):
    def __init__(self, logger, role) -> None:
        self.log = logger
        self.role = role

    def read_csv(self, file_path, id_col_name: str, label_name: str=None, sep: str=',', nrows: int=None):
        self.log.info("start load csv data from path {}".format(file_path))
        df = pandas.read_csv(file_path)
        # columns format: ID,X....,y
        columns = df.columns
        new_columns = columns.delete(columns.get_loc(id_col_name))
        # new_columns = pandas.Index([id_col_name]).append(columns)
        id_lists = df[id_col_name]
        df = df[new_columns]
        if self.role == 'host':
            if label_name:
                raise ValueError("Host party does not have label")
            return id_lists, df
        else:
            y = df[label_name]
            df.drop([label_name], axis=1, inplace=True)
            return id_lists, df, y
        

    def guest_train_test_split(self, X, y, split_ratio=0.75):
        import random
        seed = random.randint(1, 100)
        self.log.info(f"data train_test split, seed value is {seed}")
        x_train, x_test, y_train, y_test = train_test_split(X, y, train_size=split_ratio, stratify=y, random_state=seed)

        return x_train, x_test, y_train, y_test

    @staticmethod
    def read_mysql(sql):
        pass


if __name__ == "__main__":
    # Dataloader.read_csv()
    # pandas.read_csv()
    da = Dataloader('a', 'guest')
    data = pandas.read_csv('./example_data/breast_hetero_guest.csv')
    y = data['y']
    data.drop(['y'], axis=1, inplace=True)
    x_train, x_test, y_train, y_test = train_test_split(data, y, train_size=0.8, stratify=y, random_state=42)

    print(y_test)

    print(type(y_test))

    # y_test = list(map(lambda x: 1 if x ==1 else -1, y_test))
    y_test = y_test.map(lambda x: 1 if x ==1 else -1)

    print(0.5*y_test)

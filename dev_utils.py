import datetime
import pickle

import numpy
from pandas import DataFrame


def check_df(source_df: DataFrame, result_df: DataFrame, name="", detect_string_array=False) -> None:
    """
     Функция проверяет разницу между двумя датафреймами:
        - кол-во строк
        - добавились ли столбцы
        - удалились ли столбцы
        - изменились ли данные в столбцах (приводит 10 разниц значений каждого столбца)

    Example:
        check_df(source_df=data_raw, result_df=data_new, name="Name action")
    """

    def convert_str_to_list(value):
        if isinstance(value, str):
            return sorted(value.strip(separator_list).split(separator_list))
        elif isinstance(value, (numpy.ndarray, list, set)):
            return sorted(value)
        else:
            return [value]

    def convert_to_str(value):
        if isinstance(value, (numpy.ndarray, list, set)):
            return separator_list.join(sorted(value))
        else:
            return str(value)

    print("\n##### Start of analysis " + name)
    paragraph = " " * 4
    eq = "✅"
    diff = "❌"
    separator_list = ", "

    # ROWS
    difference_rows = len(result_df) - len(source_df)
    if difference_rows > 0:
        print(paragraph, diff, "Add rows:", difference_rows)
    elif difference_rows < 0:
        print(paragraph, diff, "Del rows:", abs(difference_rows))
    else:
        print(paragraph, eq, "Equal count rows")

    # COLUMNS
    columns_source = set(source_df.columns)
    columns_result = set(result_df.columns)

    new_col_df1 = columns_source - columns_result
    if new_col_df1:
        print(paragraph, diff, "Del columns:", new_col_df1)

    new_col_df2 = columns_result - columns_source
    if new_col_df2:
        print(paragraph, diff, "New columns:", new_col_df2)

    if not new_col_df1 and not new_col_df2:
        print(paragraph, eq, "Equal name columns")

    # ELEMENTS
    common_columns = columns_result & columns_source
    if difference_rows == 0 and common_columns:
        for column_name in common_columns:
            column_res = result_df[column_name]
            column_src = source_df[column_name]

            try:
                if column_res.equals(column_src):
                    print(paragraph, eq, f'Values in column "{column_name}" equal')
                    continue

                try:
                    if column_res.dtype == "array" == column_src.dtype:
                        sort_list_res = sorted(list(column_res.apply(sorted)))
                        sort_list_src = sorted(list(column_src.apply(sorted)))
                    else:
                        sort_list_res = sorted(list(column_res))
                        sort_list_src = sorted(list(column_src))
                except TypeError:  # '<' not supported between instances of 'list' and 'str'
                    sort_list_res = sorted(list(column_res.apply(convert_to_str)))
                    sort_list_src = sorted(list(column_src.apply(convert_to_str)))

                if detect_string_array and column_res.dtype == "object" == column_src.dtype:
                    try:
                        max_v_res = max(sort_list_res, key=len)
                        max_v_src = max(sort_list_src, key=len)

                        if isinstance(max_v_res, str) and separator_list in max_v_res \
                                and isinstance(max_v_src, str) and separator_list in max_v_src:
                            sort_list_res = sorted(list(column_res.apply(convert_str_to_list)))
                            sort_list_src = sorted(list(column_src.apply(convert_str_to_list)))
                            print("\n" + paragraph, f"ℹ Found an array in the string. Column {column_name}.")
                    except Exception as err:
                        print("\n" + paragraph, f"❗ Error detect string array column ({column_name}):", str(err))

                if sort_list_res == sort_list_src:
                    print(paragraph, eq, f'❗ ❗ ❗ Values in column "{column_name}" equal, but the rows have changed the order')
                else:
                    print(paragraph, diff, "Difference column", f'"{column_name}"', "(result <-> source, limit rows 10)")
                    difference_column = column_res.compare(column_src)[:10]
                    for v_res, v_src in difference_column.values:
                        print(paragraph, paragraph, v_res, "<->", v_src)
            except Exception as err:
                print("\n" + paragraph, f"🚫 Error comparison ({column_name}):", str(err))
    else:
        text = "❓ Different"
        if not difference_rows == 0:
            text += " number of rows"
        if not common_columns:
            text += " not common columns" if len(text) < 15 else "AND not common columns"
        print(paragraph, text)

    print("##### End of analysis " + name + "\n")


class TimeWatcher:
    """
        Во время инициализации фиксируется время начала. Далее с помощью функции fix_time добавляем шаги выполнения,
        после фиксации всех необходимых шагов сделайте print(obj_time_watcher).
    """

    def __init__(self):
        self._start = datetime.datetime.now()
        self._action_name = []
        self._times = []

    def fix_time(self, action_name: str):
        self._action_name.append(action_name)
        self._times.append(datetime.datetime.now())

    def __str__(self):
        paragraph = " " * 4
        text = ["##### TimeWatcher", paragraph + "Start watch " + str(self._start)]

        if self._action_name:
            max_len_action_name = len(max(self._action_name, key=len))

            delta_times: list[datetime.timedelta] = []
            prev = self._start
            for time_step in self._times:
                delta_times.append(time_step - prev)
                prev = time_step

            average_time = sum([dt.total_seconds() for dt in delta_times]) / len(delta_times)

            for action_name, time_delta in zip(self._action_name, delta_times):
                extra_spaces = ((max_len_action_name - len(action_name)) + 3) * " "
                str_td = str(time_delta) if time_delta.total_seconds() < average_time else str(time_delta) + " 🐌"
                text.append(paragraph + action_name + extra_spaces + "duration(h:m:s:ms) - " + str_td)

            text.append("\n" + paragraph + "All duration: " + str(self._times[-1] - self._start))
        else:
            text.append(paragraph + "Not steps")
        text.append("##### END TimeWatcher\n")
        return '\n'.join(text)


if __name__ == "__main__":
    # sod_orig = pickle.load(open('df_sod_dump.pkl', 'rb'))
    # new_sod = pickle.load(open('sod_new0408232200.pickle', 'rb'))

    orig = pickle.load(open('result.pkl', 'rb'))
    new = pickle.load(open('new_result.pkl', 'rb'))
    # new.to_csv('data_dm_user.csv')

    # sod_orig.to_csv("pivot_df_anomalies_dump.csv")
    # new_sod.to_csv("pivot_df_anomalies_new.csv")
    check_df(orig, new, detect_string_array=False)

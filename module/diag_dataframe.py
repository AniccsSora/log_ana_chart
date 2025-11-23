import pandas as pd
from module import dataframe_maker as df_maker


__dataframe_handler = {
    "diag_tool_info": None,
}


def add_parsed_row_into_df(command: str, row: dict, other_fields: dict) -> None:
    df = get_diag_dataframe(command)
    row = row.copy()
    other_fields = other_fields.copy()

    # auto fill non-user fill fields.
    for key, value in other_fields.items():
        row[key] = value


    # 確保 row 的所有欄位 df 都有
    keys_in_row = set(row.keys())
    keys_in_df = set(df.columns.tolist())
    if keys_in_row.issubset(keys_in_df) is False:
        missing_keys = keys_in_df - keys_in_row
        raise ValueError(f" Command:{command} 傳入的 欄位有: {keys_in_row}, 但是不滿足剩下其需要的欄位: {missing_keys} ")

    if len(row) != len(df.columns):
        raise ValueError(f" Command:{command} 傳入的 欄位數量有誤, 傳入欄位數量: {len(row)}, 但 DataFrame 需要欄位數量: {len(df.columns)} ")
    
    df.loc[len(df)] = row

def get_diag_dataframe(command: str) -> pd.DataFrame:
    if command not in __dataframe_handler:
        raise ValueError(f"Unknown command for dataframe handler: {command}")

    if __dataframe_handler[command] is None:
        if command == "diag_tool_info":
            __dataframe_handler[command] = df_maker.init_diag_tool_info_df()

    return __dataframe_handler[command]


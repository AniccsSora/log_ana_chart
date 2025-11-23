import pandas as pd
from typing import Any



def init_diag_tool_info_df() -> pd.DataFrame:
    """
    Init diag_tool_info test result dataframe to store after result.
    :return:
        pd.DataFrame
    """
    
    diag_tool_info_df = pd.DataFrame({
        "sn": pd.Series(dtype="string"),
        "test_start_time": pd.Series(dtype="datetime64[ns]"),
        "start_time": pd.Series(dtype="datetime64[ns]"),
        "end_time": pd.Series(dtype="datetime64[ns]"),
        "version": pd.Series(dtype="string"),
        "test_result": pd.Series(dtype="bool"),
    })

    # fill data into df
    # _row: dict[str, Any] = {}
    # _row["start_time"] = pd.to_datetime(res_dict["start_time"])
    # _row["end_time"] = pd.to_datetime(res_dict["end_time"])
    # _row["version"] = res_dict["test_log"][0].split(": ")[1]
    # _row["test_result"] = res_dict["pass"] == "Pass"
    #
    # diag_tool_info_df[len(diag_tool_info_df)] = _row

    return diag_tool_info_df


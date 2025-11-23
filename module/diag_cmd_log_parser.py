import module.lines_tool as lt
import pandas as pd
import module.dataframe_maker as df_maker
from typing import Callable
from typing import Any


def diag_tool_info_parser(start_time_to_end_time: list[str]) -> dict[str, Any]:
    """
[Start time: 2025-11-13 13:47:56]
Command: diag_tool_info status
Version: 1.0.0

Result: Pass
[End time: 2025-11-13 13:47:56]


[Start time: 2025-11-13 13:47:56]
Command: diag_tool_info version 1.0.0

Result: Pass
[End time: 2025-11-13 13:47:56]
    """
    lines = start_time_to_end_time
    res_dict = lt.simple_parse_single_result(lines).copy()

    logs = res_dict['test_log']
    for log in logs:
        if "Version:" in log:
            res_dict['version'] = log.split("Version:")[1].strip()
            break

    row: dict[str, Any] = {
        'start_time':  pd.to_datetime(res_dict['start_time']),
        'end_time':    pd.to_datetime(res_dict['end_time']),
        'version':     res_dict.get('version', ''),
        'test_result': res_dict['pass'] == 'Pass',
    }

    return row


parser_handler: dict[str, Callable[[list[str]], pd.DataFrame]] = {
    "diag_tool_info": diag_tool_info_parser,
}



import pandas as pd
from module import lines_tool as lt
from typing import Any

def parse_summary_from_lines(lines: list[str]) -> tuple[pd.DataFrame, dict[str, str]]:
    """
    取得 all lines 分析 summary 區塊存成 dataframe

    :param lines:
        list[str]: log file的每一行
    :return:
        tuple[pd.DataFrame, dict]: summary dataframe 和 metadata
    """
    finding: str = "=                    Summary Result                    ="
    try:
        idx = lines.index(finding)
    except ValueError as e:
        raise ValueError(f"No find {finding}") from e

    summary_start_idx = idx + 4

    summary_end_pattern = "-------------------------------------------"
    summary_end_line_idx = lt.find_next_pattern_line_number(summary_start_idx, summary_end_pattern, lines, timeout=40)

    summary_frame = pd.DataFrame({
        "Index": pd.Series(dtype="int"),
        "Command": pd.Series(dtype="string"),
        "Pass": pd.Series(dtype="int"),
        "Fail": pd.Series(dtype="int"),
        "Total": pd.Series(dtype="int")
    })

    SUMMARY_START_TIME = "Start Time"
    SUMMARY_END_TIME = "End Time"
    SUMMARY_TEST_DURATION = "Test Duration"
    SUMMARY_TEST_RESULT = "Test Result"
    SUMMARY_KERNEL_VERSION = "Kernel Version"
    SUMMARY_SOFTWARE_VERSION = "Software version"
    SUMMARY_DIAG_TOOL_VERSION = "Diag Tool Version"
    
    summary_meta = {
        SUMMARY_START_TIME: "",
        SUMMARY_END_TIME: "",
        SUMMARY_TEST_DURATION: "",
        SUMMARY_TEST_RESULT: "",
        SUMMARY_KERNEL_VERSION: "",
        SUMMARY_SOFTWARE_VERSION: "",
        SUMMARY_DIAG_TOOL_VERSION: "",
    }

    # get each summary meta line idx
    summary_start_time_line_idx = lt.find_next_pattern_line_number(summary_end_line_idx, SUMMARY_START_TIME, lines, timeout=10)
    summary_end_time_line_idx = lt.find_next_pattern_line_number(summary_end_line_idx, SUMMARY_END_TIME, lines, timeout=10)
    summary_test_dur_line_idx = lt.find_next_pattern_line_number(summary_end_line_idx, SUMMARY_TEST_DURATION, lines, timeout=10)
    summary_test_res_line_idx = lt.find_next_pattern_line_number(summary_end_line_idx, SUMMARY_TEST_RESULT, lines, timeout=10)
    summary_kernel_ver_line_idx = lt.find_next_pattern_line_number(summary_end_line_idx, SUMMARY_KERNEL_VERSION, lines, timeout=10)
    summary_sw_version_line_idx = lt.find_next_pattern_line_number(summary_end_line_idx, SUMMARY_SOFTWARE_VERSION, lines, timeout=10)
    summary_diag_tool_version_line_idx = lt.find_next_pattern_line_number(summary_end_line_idx, SUMMARY_DIAG_TOOL_VERSION, lines, timeout=10)

    # save summary metadata
    summary_meta[SUMMARY_START_TIME] = lines[summary_start_time_line_idx].strip().split(': ')[1]
    summary_meta[SUMMARY_END_TIME] = lines[summary_end_time_line_idx].strip().split(': ')[1]
    summary_meta[SUMMARY_TEST_DURATION] = lines[summary_test_dur_line_idx].strip().split(': ')[1]
    summary_meta[SUMMARY_TEST_RESULT] = lines[summary_test_res_line_idx].strip().split(': ')[1]
    summary_meta[SUMMARY_KERNEL_VERSION] = lines[summary_kernel_ver_line_idx].strip().split(': ')[1]
    summary_meta[SUMMARY_SOFTWARE_VERSION] = lines[summary_sw_version_line_idx].strip().split(': ')[1]
    summary_meta[SUMMARY_DIAG_TOOL_VERSION] = lines[summary_diag_tool_version_line_idx].strip().split(': ')[1]

    for i in range(summary_start_idx, summary_end_line_idx):
        try:
            _idx, _cmd, p, f, t = lines[i].strip().split()
        except ValueError as e:
            _example = "1      diag_tool_info                  122   0     122"
            print(f"Parse summary row error: '{lines[i]}'")
            print(f"     expected like below:'{_example}'")
            continue
            
        be_added_row: dict[str, Any] = {
            "Index": int(_idx),
            "Command": _cmd,
            "Pass": int(p),
            "Fail": int(f),
            "Total": int(t)
        }
        summary_frame.loc[len(summary_frame)] = be_added_row

    # 檢查任何 total 計數 有不一致的現象
    if len(summary_frame) > 0:
        _first = summary_frame["Total"].iloc[0]
        total_val_all = summary_frame["Total"] == _first

        if not total_val_all.all():
            for _idx, is_consistent in enumerate(total_val_all):
                print(_idx + 1, is_consistent, summary_frame["Command"].iloc[_idx])
            raise ValueError("發現不一致的 total 統計 總數, 所有測試項目的 summary total 都應該一樣。")

    return summary_frame, summary_meta





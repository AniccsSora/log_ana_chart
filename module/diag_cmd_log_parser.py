import module.lines_tool as lt

def diag_tool_info_parser(start_time_to_end_time: list):
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
    print("start")
    print(lines)
    rr = lt.simple_parse_single_result(lines)
    print(rr)

    print("end")


parser_handler = {
    "diag_tool_info": diag_tool_info_parser,
}
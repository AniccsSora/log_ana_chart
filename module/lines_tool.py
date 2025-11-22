def find_next_pattern_line_number(start: int, pattern: str, lines: list[str], timeout: int):
    """
    從 lines 的 start 行開始找, 找到包含 pattern 的行號, 找不到就丟錯誤，行號都基於
    傳入的 List 為準。
    :param start: 起找的 List idx
    :param pattern: 字串 pattern
    :param lines: List[str]
    :param timeout: 以起找 start 行開始，如過了 timout 行 仍未找到， raise ValueError
    :return:
    """
    cnt, limit = 0, timeout
    _find_log = []
    while cnt < limit:
        _find_log.append(lines[start+cnt])
        if pattern in lines[start+cnt]:
            return start+cnt
        cnt += 1
    _log = "\n".join(_find_log)
    raise ValueError("沒找到 pattern = `{}`, 從第 {} 行開找, 找了 {} 行找無, log:\n{}".format(pattern, start, limit, _log))


def read_log_file_as_lines(file_path):
    with open(file_path, encoding='utf-8') as f:
        lines = [_.rstrip('\n')for _ in f.readlines()]

    return lines


def simple_parse_single_result(in_res: list) -> dict:
    """
    Analyze the log list of a single test result and extract key information.

    Args:
        in_res:
            [
                '[Start time: 2025-11-20 18:58:01]',
                'Command: diag_tool_info status',
                'Version: 1.0.0',
                '',
                'Result: Pass',
                '[End time: 2025-11-20 18:58:01]',
            ]

    Returns:
        dict:
            - start_time: str
            - command: str
            - command_option: str
            - test_log: list[str]
            - pass: str
    """
    result = {
        'start_time': '',
        'end_time': '',
        'command': '',
        'command_option': '',
        'test_log': [],
        'pass': ''
    }

    start_time_detected = 0
    end_time_detected = 0

    for line in in_res:
        line = line.strip()

        # Parse time
        if line.startswith('[Start time:'):
            # 移除 '[Start time: ' 和 ']'
            result['start_time'] = line[13:-1].strip()
            start_time_detected = 1

        elif line.startswith('[End time:'):
            # 移除 '[Start time: ' 和 ']'
            result['end_time'] = line[13:-1].strip()
            end_time_detected = 1

        # Parse commnd
        elif line.startswith('Command:'):
            command_parts = line[8:].strip().split(maxsplit=1)
            result['command'] = command_parts[0] if command_parts else ''
            result['command_option'] = command_parts[1] if len(command_parts) > 1 else ''

        # Parse result
        elif line.startswith('Result:'):
            result['pass'] = line[7:].strip()

        # skip null line
        elif line == '':
            continue

        # 其餘內容加入 test_log
        else:
            result['test_log'].append(line)

    if end_time_detected == 0 or start_time_detected == 0:
        for line in in_res:
            print(line)
        raise ValueError("Log format error: Missing start time or end time.")
    return result



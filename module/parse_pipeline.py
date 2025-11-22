from abc import ABC, abstractmethod
from module import lines_tool as lt
from module import diag_cmd_log_parser as diag_log_parser

class ALEParserPipeLineI(ABC):
    def __init__(self):
        self.summary_df = None
        pass

    def run(self):
        # self.step_1_get_single_round_seq()
        self.step_0_parse_start_time_string()

    @abstractmethod
    def step_0_parse_start_time_string(self): pass


class ALEParserPipeLine(ALEParserPipeLineI):
    def __init__(self, lines, summary_df):
        self.lines = lines.copy()
        self.lines_max = len(self.lines)
        self.summary_df = summary_df
        self._cpl = 0  # current parser line
        self.generator_diag_cmd = self.get_diag_cmd_generator()
        self.run()
        self.base_on_diag_cmd_seq_to_patser()

    def step_0_parse_start_time_string(self):
        pattern = "Diag test starts at"
        idx = lt.find_next_pattern_line_number(0, pattern, self.lines, 20)
        self.lines[idx]
        self.parsed_start_time = self.lines[idx].split(pattern)[1].strip()

    def get_diag_cmd_generator(self):
        while True:
            yield from self.summary_df["Command"].tolist()

    def get_next_diag_cmd(self):
        return next(self.generator_diag_cmd)

    def base_on_diag_cmd_seq_to_patser(self):
        dev_cnt_limit = 100  # dev
        while self._cpl < self.lines_max:
            start = self._cpl
            _diag_cmd = self.get_next_diag_cmd()
            pattern = "Command: " + _diag_cmd
            # print(f"cpl[{self._cpl+1}] search cmd = {pattern}")
            start = lt.find_next_pattern_line_number(start, pattern, self.lines, 10)
            start -= 1  # 去包含上一行  start time
            # print("start line =", lines[start])

            end_pattern = "Result: "
            end = lt.find_next_pattern_line_number(start, end_pattern, self.lines, 100)
            end += 2  # 去包含到後面的 end t ime
            # print(">>>>>>>>>>>>>>>>>>>")
            # print(lines[start:end])
            # print("<<<<<<<<<<<<<<<<<<<")
            parser_func = diag_log_parser.parser_handler[_diag_cmd]
            single_test_result = self.lines[start:end]
            parser_func(single_test_result)

            raise ValueError("No implement")

            if self._cpl > dev_cnt_limit:  # dev
                break  # dev
            # update
            self._cpl = end
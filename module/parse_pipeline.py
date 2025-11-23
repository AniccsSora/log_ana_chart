from abc import ABC, abstractmethod
from module import lines_tool as lt
from module import diag_cmd_log_parser as diag_log_parser
import pandas as pd
from typing import Generator, Callable
from module import diag_dataframe as dd
from module import diag_defines as dd_defs

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
    def __init__(self, lines: list[str], summary_df: pd.DataFrame, summary_meta: dict, sn: str):
        self.lines = lines.copy()
        self.diag_result_df = {}
        self.sn = sn
        self.log_start_time = pd.to_datetime(summary_meta["Start Time"])
        self.lines_max = len(self.lines)
        self.diag_params_table = dd_defs.diag_cmd_def
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

    def get_diag_cmd_generator(self) -> Generator[str, None, None]:
        while True:
            yield from self.summary_df["Command"].tolist()

    def get_next_diag_cmd(self) -> str:
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
            _timeout = self.diag_params_table[_diag_cmd]["timeout"]
            end = lt.find_next_pattern_line_number(start, end_pattern, self.lines, _timeout)
            end += 2  # 去包含到後面的 end t ime

            try:
                parser_func: Callable = diag_log_parser.parser_handler[_diag_cmd]
            except KeyError:
                print(f"Warning: No parser func for diag cmd = {_diag_cmd}, skip it.")
                self._cpl = end
                continue

            diag_test_session_log: list[str] = self.lines[start:end]
            # 尋找特定的 diag_cmd func 來 parse
            _parsed_row = parser_func(diag_test_session_log)
            _common_fields = { "sn": self.sn, "test_start_time": self.log_start_time }
            try:
                dd.add_parsed_row_into_df(_diag_cmd, _parsed_row, _common_fields)
            except Exception as e:
                print("Error when add parsed row into df:", e)
#            raise ValueError("No implement")

            if self._cpl > dev_cnt_limit:  # dev
                break  # dev
            # update
            self._cpl = end
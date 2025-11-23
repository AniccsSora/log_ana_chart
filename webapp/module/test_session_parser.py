"""
測試項目解析器
解析 diag log 中的每個測試 session
"""
import re
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class TestSession:
    """單一測試項目的資料結構"""
    start_time: str
    end_time: str
    command: str
    command_name: str  # 提取的 diag command 名稱
    result: str  # Pass, Fail, Exception
    temperature: Optional[float]  # 溫度 (如果有)
    group_name: str  # test1, test2...
    round_number: int  # 第幾輪
    log_content: List[str]  # 完整的 log 內容
    duration_seconds: Optional[float]  # 執行時間 (秒)
    
    def __post_init__(self):
        """計算執行時間"""
        if self.start_time and self.end_time:
            try:
                fmt = "%Y-%m-%d %H:%M:%S"
                start = datetime.strptime(self.start_time, fmt)
                end = datetime.strptime(self.end_time, fmt)
                self.duration_seconds = (end - start).total_seconds()
            except:
                self.duration_seconds = None


class DiagLogParser:
    """Diag log 解析器"""
    
    # 正則表達式模式
    PATTERN_TEST_START = r"Diag test starts at (.+)"
    PATTERN_RUN_GROUP = r"Run \[(.+?)\] command group \[Round (\d+)\]"
    PATTERN_START_TIME = r"\[Start time: (.+?)\]"
    PATTERN_END_TIME = r"\[End time: (.+?)\]"
    PATTERN_COMMAND = r"Command: (.+)"
    PATTERN_RESULT_PASS = r"Result: Pass"
    PATTERN_RESULT_FAIL = r"Result: Fail(?:\s*\((.+?)\s*deg\s*C\))?"
    
    def __init__(self, lines: List[str]):
        self.lines = lines
        self.current_line = 0
        self.test_start_time = None
        self.current_group = None
        self.current_round = 1
        self.sessions: List[TestSession] = []
        
    def parse(self) -> List[TestSession]:
        """解析整個 log 檔案"""
        # 1. 取得測試開始時間
        self._parse_test_start_time()
        
        # 2. 逐行掃描並解析每個 session
        while self.current_line < len(self.lines):
            # 檢查是否有新的 group/round 資訊
            self._update_group_info()
            
            # 檢查是否是 session 開始
            session = self._try_parse_session()
            if session:
                self.sessions.append(session)
            else:
                self.current_line += 1
                
        return self.sessions
    
    def _parse_test_start_time(self):
        """解析測試開始時間"""
        for i, line in enumerate(self.lines[:100]):  # 只掃描前100行
            match = re.search(self.PATTERN_TEST_START, line)
            if match:
                self.test_start_time = match.group(1).strip()
                break
    
    def _update_group_info(self):
        """更新當前的 group 和 round 資訊"""
        if self.current_line >= len(self.lines):
            return
            
        line = self.lines[self.current_line]
        match = re.search(self.PATTERN_RUN_GROUP, line)
        if match:
            self.current_group = match.group(1)
            self.current_round = int(match.group(2))
            self.current_line += 1
    
    def _try_parse_session(self) -> Optional[TestSession]:
        """嘗試解析一個 session"""
        if self.current_line >= len(self.lines):
            return None
            
        line = self.lines[self.current_line]
        
        # 檢查是否是 session 開始
        start_match = re.search(self.PATTERN_START_TIME, line)
        if not start_match:
            return None
        
        start_time = start_match.group(1).strip()
        session_start_line = self.current_line
        self.current_line += 1
        
        # 收集 session 的所有行，直到遇到 Result 或檔案結束
        session_lines = [self.lines[session_start_line]]
        command = None
        command_name = None
        result = "Exception"
        temperature = None
        end_time = None
        
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]
            session_lines.append(line)
            
            # 解析 Command
            if command is None:
                cmd_match = re.search(self.PATTERN_COMMAND, line)
                if cmd_match:
                    command = cmd_match.group(1).strip()
                    command_name = command.split()[0] if command else ""
            
            # 檢查 Result: Pass
            if re.search(self.PATTERN_RESULT_PASS, line):
                result = "Pass"
                self.current_line += 1
                
                # 尋找 End time
                if self.current_line < len(self.lines):
                    end_line = self.lines[self.current_line]
                    session_lines.append(end_line)
                    end_match = re.search(self.PATTERN_END_TIME, end_line)
                    if end_match:
                        end_time = end_match.group(1).strip()
                    self.current_line += 1
                break
            
            # 檢查 Result: Fail
            fail_match = re.search(self.PATTERN_RESULT_FAIL, line)
            if fail_match:
                result = "Fail"
                # 提取溫度 (如果有)
                if fail_match.group(1):
                    try:
                        temperature = float(fail_match.group(1))
                    except:
                        pass
                
                self.current_line += 1
                
                # 尋找 End time
                if self.current_line < len(self.lines):
                    end_line = self.lines[self.current_line]
                    session_lines.append(end_line)
                    end_match = re.search(self.PATTERN_END_TIME, end_line)
                    if end_match:
                        end_time = end_match.group(1).strip()
                    self.current_line += 1
                break
            
            self.current_line += 1
            
            # 防止無限循環：如果遇到下一個 session 開始，就停止
            if re.search(self.PATTERN_START_TIME, line) and len(session_lines) > 1:
                session_lines.pop()  # 移除下一個 session 的開始行
                break
        
        # 創建 TestSession 物件
        return TestSession(
            start_time=start_time,
            end_time=end_time or "Unknown",
            command=command or "Unknown",
            command_name=command_name or "Unknown",
            result=result,
            temperature=temperature,
            group_name=self.current_group or "Unknown",
            round_number=self.current_round,
            log_content=session_lines,
            duration_seconds=None  # 會在 __post_init__ 中計算
        )
    
    def get_failed_sessions(self) -> List[TestSession]:
        """取得所有失敗的 sessions"""
        return [s for s in self.sessions if s.result == "Fail"]
    
    def get_exception_sessions(self) -> List[TestSession]:
        """取得所有異常的 sessions (沒有 Result)"""
        return [s for s in self.sessions if s.result == "Exception"]
    
    def get_passed_sessions(self) -> List[TestSession]:
        """取得所有通過的 sessions"""
        return [s for s in self.sessions if s.result == "Pass"]


def parse_diag_log(lines: List[str]) -> dict:
    """
    解析 diag log 並返回結構化資料
    
    Args:
        lines: log 檔案的每一行
        
    Returns:
        dict: 包含解析結果的字典
    """
    parser = DiagLogParser(lines)
    parser.parse()
    
    failed_sessions = parser.get_failed_sessions()
    exception_sessions = parser.get_exception_sessions()
    passed_sessions = parser.get_passed_sessions()
    
    return {
        'test_start_time': parser.test_start_time,
        'total_sessions': len(parser.sessions),
        'passed_count': len(passed_sessions),
        'failed_count': len(failed_sessions),
        'exception_count': len(exception_sessions),
        'failed_sessions': failed_sessions,
        'exception_sessions': exception_sessions,
        'passed_sessions': passed_sessions,
        'all_sessions': parser.sessions
    }

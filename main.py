import sys
from module import lines_tool as lt
from module.parse_pipeline import ALEParserPipeLine
from module.log_parser import parse_summary_from_lines


def main():
    lines = lt.read_log_file_as_lines("./logs/TLN25460001P_20251120_18_58_00_fail_IDX_00015.log")
    summary_frame, summary_meta = parse_summary_from_lines(lines)
    ale_parser = ALEParserPipeLine(lines, summary_frame)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("Error:", e)
        sys.exit(1)


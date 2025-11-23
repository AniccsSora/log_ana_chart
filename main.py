import sys
from module import lines_tool as lt
from module.parse_pipeline import ALEParserPipeLine
from module.log_parser import parse_summary_from_lines
from module import diag_dataframe
from pathlib import Path
import traceback

def main():
    file_path = "./logs/TLN25460001P_20251120_18_58_00_fail_IDX_00015.log"
    lines = lt.read_log_file_as_lines(file_path)
    sn = Path(file_path).stem.split("_")[0]
    summary_frame, summary_meta = parse_summary_from_lines(lines)
    ale_parser = ALEParserPipeLine(lines, summary_frame, summary_meta, sn)
    print("fufu")

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        #print("Error:", e)
        traceback.print_exc()
        sys.exit(1)


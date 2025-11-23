

def dump_log(lines):
    print("前10行:")
    for i, line in enumerate(lines[:10], 1):
        print(f"{i}: {line}")
    print("\n後10行:")
    for i, line in enumerate(lines[-10:], 1):
        print(f"{i}: {line}")
    print("=" * 50)
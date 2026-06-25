f = open("src/main_dating.py", "r", encoding="utf-8")
lines = f.readlines()
f.close()
print(f"Total lines: {len(lines)}")
# Найти строку с h_start
for i, line in enumerate(lines):
    if "async def h_start(m: Message)" in line:
        print(f"Found h_start at line {i+1}: {line[:60]}")
    if "async def h_onboarding_text" in line:
        print(f"Found h_onboarding_text at line {i+1}: {line[:60]}")
    if "async def ask_age" in line:
        print(f"Found ask_age at line {i+1}: {line[:60]}")

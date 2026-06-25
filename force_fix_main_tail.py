# force_fix_main_tail.py — вырезает хвост от последнего if __name__ == "__main__": и вставляет правильный блок
import pathlib, re, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Нормализация символов
s = (s.replace("\","")
       .replace("\ "," ")
       .replace("\r","")
       .replace("\t","    "))

# Найти ПОСЛЕДНЕЕ вхождение if __name__ == "__main__":
m = None
for m2 in re.finditer(r'(?m)^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:\s*', s):
    m = m2

# Сформировать правильный блок
tail = (
    "if __name__ == \"__main__\":\n"
    "    import asyncio\n"
    "    print(\"Bot is starting...\")\n"
    "    asyncio.run(main())\n"
)

if m:
    # Обрезаем всё после последнего if и вставляем хвост
    s = s[:m.start()] + tail
else:
    # Если блока нет — просто добавим в конец с пустой строкой
    if not s.endswith("\n"):
        s += "\n"
    s += "\n" + tail

# Бэкап и запись
shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: хвост main.py перезаписан корректно (backup: src/main.py.bak)")

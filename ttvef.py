with open("set_data_git\\dex_data.json", "r", encoding="utf-8-sig") as f:
    content = f.read()

with open("set_data_git\\dex_data.json", "w", encoding="utf-8") as f:
    f.write(content)
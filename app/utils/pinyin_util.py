from pypinyin import lazy_pinyin
def chinese_to_pinyin_keep_others(text):
    result = []
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':  # 是中文汉字
            result.extend(lazy_pinyin(ch))
        else:
            result.append(ch)
    return ''.join(result)
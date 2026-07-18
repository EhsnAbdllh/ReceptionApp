def to_persian_digits(text):
    if text is None:
        return ""
    text = str(text)
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    table = str.maketrans(english_digits, persian_digits)
    return text.translate(table)

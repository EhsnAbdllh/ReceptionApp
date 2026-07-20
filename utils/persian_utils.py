def to_persian_digits(text):
    if text is None:
        return ""
    text = str(text)
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    table = str.maketrans(english_digits, persian_digits)
    return text.translate(table)

def to_english_digits(text):
    if text is None:
        return ""
    text = str(text)
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"
    table_persian = str.maketrans(persian_digits, english_digits)
    table_arabic = str.maketrans(arabic_digits, english_digits)
    return text.translate(table_persian).translate(table_arabic)


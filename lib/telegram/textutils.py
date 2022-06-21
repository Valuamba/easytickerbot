MARKDOWN_CHARS_TO_ESCAPE = [
    "_",
    "*",
    "[",
    "]",
    "(",
    ")",
    "~",
    "`",
    ">",
    "#",
    "+",
    "-",
    "=",
    "|",
    "{",
    "}",
    ".",
    "!",
]


def escape_markdown(text):
    for char_to_escape in MARKDOWN_CHARS_TO_ESCAPE:
        text = str(text).replace(char_to_escape, f"\\{char_to_escape}")
    return text

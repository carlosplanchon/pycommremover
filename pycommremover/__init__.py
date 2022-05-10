#!/usr/bin/env python3


def _get_comments_symbol(text: str, symbol: str) -> list[str]:
    comments = []
    i: int = 0
    indexes = []
    for i in range(len(text)):
        if text[i] == symbol:
            if len(text) > i + 2:
                if text[i] == text[i + 1] == text[i + 2]:
                    # print("Triple quote.")
                    if(len(indexes) == 0):
                        indexes.append(i)
                    elif len(indexes) == 1:
                        indexes.append(i + 2)
                        comments.append(text[indexes[0]: indexes[1] + 1])
                        indexes = []

    return comments


def _get_comments_simplequot(text: str) -> list[str]:
    return _get_comments_symbol(text=text, symbol="'")


def _get_comments_doublequot(text: str) -> list[str]:
    return _get_comments_symbol(text=text, symbol='"')


def remove_comments(text: str) -> str:
    comments = _get_comments_simplequot(text=text)
    for comment in comments:
        text = text.replace(comment, "")

    comments = _get_comments_doublequot(text=text)
    for comment in comments:
        text = text.replace(comment, "")

    lines = text.split("\n")

    new_lines = []

    for line in lines:
        if "#" in line:
            line_without_comment = "#".join(line.split("#")[:1]).rstrip(" ")
            new_lines.append(line_without_comment)
        else:
            new_lines.append(line)

    text = "\n".join(new_lines)
    # print("--- TEXT ---")
    # print(text)
    return text

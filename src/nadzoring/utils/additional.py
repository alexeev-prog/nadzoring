"""Additional utility functions."""


def grep_in_line(text: str, filter_key: str | list[str], split_symbol: str = "\n") -> list[str]:
    r"""Filter lines by key(s).

    Args:
        text (str): full text.
        filter_key (str | list[str]): key or list of keys for filtering.
        split_symbol (str, optional): symbol for splitting into lines. Defaults to "\n".

    Returns:
        list[str]: matches.
    """
    if isinstance(filter_key, str):
        filter_key = [filter_key]

    return [line for line in text.strip().split(split_symbol) if any(key in line for key in filter_key)]

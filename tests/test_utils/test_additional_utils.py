from nadzoring.utils.additional import grep_in_line


def test_grep_in_line_simple():
    assert grep_in_line("hello world\nbye bye\nel psy congroo\nworld hello", "world") == ["hello world", "world hello"]


def test_grep_in_line_custom_split():
    assert grep_in_line("hello worldXXXbye byeXXXel psy congrooXXXworld hello", "world", "XXX") == [
        "hello world",
        "world hello",
    ]


def test_grep_in_line_multiple_keys():
    """Test filtering with multiple keys."""
    text = "hello world\nbye bye\nel psy congroo\nworld hello\nhello there\ngoodbye"
    result = grep_in_line(text, filter_key=["hello", "goodbye"])
    assert result == ["hello world", "world hello", "hello there", "goodbye"]


def test_grep_in_line_no_matches():
    """Test when no lines match the filter key."""
    text = "hello world\nbye bye\nel psy congroo"
    result = grep_in_line(text, filter_key="nonexistent")
    assert result == []


def test_grep_in_line_empty_text():
    """Test with empty text input."""
    result = grep_in_line("", filter_key="world")
    assert result == []


def test_grep_in_line_whitespace_only():
    """Test with whitespace-only text."""
    result = grep_in_line("   \n   \n   ", filter_key="world")
    assert result == []


def test_grep_in_line_single_line():
    """Test with single line text."""
    result = grep_in_line("hello world", filter_key="world")
    assert result == ["hello world"]


def test_grep_in_line_multiple_keys_no_matches():
    """Test with multiple keys where none match."""
    text = "hello world\nbye bye\nel psy congroo"
    result = grep_in_line(text, filter_key=["foo", "bar"])
    assert result == []


def test_grep_in_line_multiple_keys_with_duplicates():
    """Test with multiple keys that may overlap."""
    text = "hello world\nhello there\nworld hello\ngoodbye world"
    result = grep_in_line(text, filter_key=["hello", "world"])
    assert result == ["hello world", "hello there", "world hello", "goodbye world"]


def test_grep_in_line_empty_filter_key():
    """Test with empty filter key string."""
    text = "hello world\nbye bye"
    result = grep_in_line(text, filter_key="")
    assert result == ["hello world", "bye bye"]


def test_grep_in_line_empty_filter_key_list():
    """Test with empty list as filter_key."""
    text = "hello world\nbye bye"
    result = grep_in_line(text, filter_key=[])
    assert result == []


def test_grep_in_line_case_sensitive():
    """Test that filtering is case-sensitive."""
    text = "Hello world\nhello world\nHELLO world"
    result = grep_in_line(text, filter_key="hello")
    assert result == ["hello world"]

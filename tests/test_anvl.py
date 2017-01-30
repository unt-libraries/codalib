import pytest

from codalib import anvl


class Test_readANVLString(object):
    def test_with_empty_string(self):
        """
        Check that readANVLString can handle an empty string.
        """
        actual = anvl.readANVLString('')
        expected = {}
        assert actual == expected

    def test_with_simple_anvl_string(self):
        """
        Check that readANVLString parses single key value.
        """
        actual = anvl.readANVLString('key:value')
        expected = {'key': 'value'}
        assert actual == expected

    def test_strips_left_whitespace_of_value(self):
        """
        Check that readANVLString only strips whitespace on the left side
        of the value.
        """
        actual = anvl.readANVLString('key: value ')
        expected = {'key': 'value '}
        assert actual == expected

    def test_string_without_colon(self):
        """
        Verifies malformed ANVL records raise anvl.InvalidANVLRecord
        exception.
        """
        with pytest.raises(anvl.InvalidANVLRecord):
            anvl.readANVLString('foo bar baz qux')

    def test_with_comment(self):
        """
        Verify readANVLString can handle a comment with the `#` char
        in the first column of a line.
        """
        anvl_string = (
            """# this is comment\n
            key1: value1\n
            key2: value2\n
            """
        )

        actual = anvl.readANVLString(anvl_string)
        expected = {'key1': 'value1', 'key2': 'value2'}
        assert actual == expected

    @pytest.mark.xfail
    def test_with_comment_char_not_in_first_column(self):
        """
        readANVLString should be able to pickup a comment char even
        if whitespace precedes it.  This test verifies the function's
        behavior, but it has been marked as an expected failure because
        it is not the desired functionality.
        """
        anvl_string = '\t# this is comment\n'

        with pytest.raises(IndexError):
            anvl.readANVLString(anvl_string)

    def test_with_empty_lines(self):
        """
        Check that readANVLString can handle empty lines.
        """
        anvl_string = ('key1: value1\n'
                       '\n'
                       'key2: value2\n')

        actual = anvl.readANVLString(anvl_string)
        expected = {'key1': 'value1', 'key2': 'value2'}

        assert actual == expected

    def test_captures_buffered_content(self):
        """
        Verify that readANVLString parses values that wrap to the next
        line.
        """
        anvl_string = ('key: Buffered\n'
                       '     Content\n')

        actual = anvl.readANVLString(anvl_string)
        expected = {'key': 'Buffered Content'}
        assert actual == expected


class Test_breakString(object):
    def test_breakString_breaks_line(self):
        """
        Verify breakString inserts a line break at the correct index.
        """
        string = 'This string should have newline after the word "newline"'
        output = anvl.breakString(string, width=31)
        assert '\n' == output[31]

    def test_breakString_offset(self):
        """
        Check breakString with the width and firstLineOffset kwargs.
        """
        string = 'This is the first line this is the second line'
        output = anvl.breakString(string, width=22, firstLineOffset=10)
        lines = output.split('\n')

        assert len(lines) == 3
        assert len(lines[0]) == 11
        assert len(lines[1]) == 19


class Test_writeANVLString(object):
    def test_output_is_valid_ANVL(self):
        """
        Verify the output of writeANVLString is ANVL.
        """
        input_dict = dict(foo='bar', baz='qux')

        actual = anvl.writeANVLString(input_dict)
        expected = 'baz: qux\nfoo: bar'

        assert actual == expected

    def test_with_empty_dict(self):
        """
        Verify writeANVLString with empty input.
        """
        input_dict = dict()
        output = anvl.writeANVLString(input_dict)
        assert output == ''

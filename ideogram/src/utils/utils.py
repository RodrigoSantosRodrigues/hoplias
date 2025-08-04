def format_text_as_html(text):
    """
    Converts a text into HTML, wrapping each line in a <p> tag.

    Args:
        text (str): Input text.

    Returns:
        str: Text formatted as HTML.
    """
    lines = text.split('\n')
    html = ''.join(f'<p>{line}</p>' for line in lines)
    return html


ALLOWED_EXTENSIONS = set(['json'])


def allowed_file(filename):
    """check if the filename is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

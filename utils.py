from pathlib import Path

def get_version():
    """
    Returns:
        content of version file
    """
    version_file = Path(__file__).parent / "version"
    with open(version_file, "r") as version_content:
        return version_content.read()

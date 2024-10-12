import os
import re

from setuptools import setup


def get_version():
    version_file = os.path.join("dj_waanverse_auth", "version.py")
    with open(version_file) as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            version = version_match.group(1)
            print(version)
            return version
        raise RuntimeError("Unable to find version string.")


if __name__ == "__main__":
    setup(version=get_version())

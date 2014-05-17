#!/usr/bin/env python
import os
import sys

grandparent_dir = os.path.abspath(os.path.join(os.path.abspath(os.path.splitext(__file__)[0]), '../..'))
sys.path.insert(0, grandparent_dir)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

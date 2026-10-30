# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

# Pytest rewrites test imports before Beartype's package hook can run.
# conftest.py decorates collected tests instead, and helpers use explicit decorators.

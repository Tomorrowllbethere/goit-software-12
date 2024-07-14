# test_imports.py
import os
import sys
# Додайте шлях до кореневого каталогу вашого проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from str.conf.config import settings
    print("Settings imported successfully")
    print(settings.algorithm)
    print(f'\n -------\n{settings.model_dump()}\n-------')
except ImportError as e:
    print(f"Error importing settings: {e}")

try:
    from str.routes import auth
    print("Routes auth imported successfully")
    from str.routes import notes
    print("Routes notes auth imported successfully")
    from str.routes import users
    print("Routes users imported successfully")

except ImportError as e:
    print(f"Error importing routes: {e}")


#                   py tests/test_imports.py

'''
Renames emoji files in a directory based on their Unicode names.

This script uses the 'emoji' library to find the official CLDR (Common
Locale Data Repository) short name for an emoji and renames the file
accordingly. For example, a file named '1f600.png' will be renamed to
'grinning_face.png'.

It handles single codepoints, multi-codepoint sequences (like flags),
and skin tone modifiers.

Files that are not named with valid Unicode codepoints will be skipped.
'''
import os
import sys


def install_and_import(package):
    """Try to import a package, installing it if it fails."""
    try:
        return __import__(package)
    except ImportError:
        print(f"'{package}' library not found. Attempting to install...")
        try:
            import pip
            pip.main(['install', package])
        except Exception as e:
            print(f"Could not install '{package}'. Error: {e}")
            print(f"Please install it manually: pip install {package}")
            sys.exit(1)
    return __import__(package)

def rename_emoji_files():
    """Renames all emoji files in the 'emojis' directory."""
    emoji = install_and_import('emoji')

    emoji_dir = os.path.join(os.path.dirname(__file__), 'emojis')
    if not os.path.isdir(emoji_dir):
        print(f"Error: Directory not found at '{emoji_dir}'")
        return

    print(f"Scanning for emojis in: {emoji_dir}")
    filenames = os.listdir(emoji_dir)
    skipped_files = []

    for filename in filenames:
        old_path = os.path.join(emoji_dir, filename)
        if not os.path.isfile(old_path):
            continue

        name_part, extension = os.path.splitext(filename)
        if not extension == '.png':
            continue

        try:
            # Convert hex codepoints to an emoji character
            codepoints = name_part.split('-')
            char = ''.join(chr(int(code, 16)) for code in codepoints)

            # Demojize to get the CLDR short name (e.g., :grinning_face:)
            demojized_name = emoji.demojize(char, delimiters=('', ''))

            if demojized_name == char:
                # If demojize returns the original char, it's not a standard emoji
                raise ValueError("Not a standard emoji character")

            # Sanitize the name for a filename
            new_name = demojized_name.replace('_', '-').replace(':', '')
            new_filename = f"{new_name}{extension}"
            new_path = os.path.join(emoji_dir, new_filename)

            if old_path == new_path:
                continue

            print(f"Renaming: {filename} -> {new_filename}")
            os.rename(old_path, new_path)

        except (ValueError, TypeError):
            skipped_files.append(filename)
            continue

    if skipped_files:
        print("\n--- Skipped Files ---")
        print("Could not process the following files:")
        for fname in skipped_files:
            print(f"- {fname}")

if __name__ == "__main__":
    rename_emoji_files()

"""
Pandoc Markdown to PDF Compiler with Watch Mode

This module provides functionality to compile Markdown files to PDF using Pandoc
with Beamer template, including file watching capabilities and Unicode character
replacement.
"""

import os
import contextlib
import time
import hashlib
import argparse
import tempfile

import sh

PANDOC_CMD_TEMPLATE = sh.Command("pandoc").bake(t="beamer")

REPLACES = {
    "≠": r"$\neq$",
}


@contextlib.contextmanager
def chdir(newdir):
    """
    Context manager to temporarily change the working directory.

    Parameters
    ----------
    newdir : str
        Path to the new directory to change to.

    Yields
    ------
    None
        Control is yielded while in the new directory.

    Examples
    --------
    >>> with chdir('/tmp'):
    ...     print(os.getcwd())
    /tmp
    """
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def get_parser():
    """
    Create and configure the command line argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser with all required arguments and options.

    Examples
    --------
    >>> parser = get_parser()
    >>> args = parser.parse_args(['file.md', '--watch'])
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "archivo",
        help="ruta del archivo a compilar",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--sleep",
        help="segundos de espera",
        action="store",
        type=float,
        default=1.5,
    )
    parser.add_argument("-w", "--watch", help="watch mode", action="store_true", default=False)
    parser.add_argument("-i", "--ignore_error", action="store_false", default=True)
    parser.add_argument(
        "--cd",
        help="cambiar al directorio del archivo",
        action="store_true",
        default=True,
    )
    return parser


def read_file(path):
    """
    Read the contents of a file.

    Parameters
    ----------
    path : str
        Path to the file to read.

    Returns
    -------
    str
        Contents of the file as a string.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    IOError
        If there's an error reading the file.

    Examples
    --------
    >>> content = read_file('example.md')
    >>> print(len(content))
    1234
    """
    with open(path, "r") as f:
        return f.read()


def calculate_md5(src):
    """
    Calculate the MD5 hash of a string.

    Parameters
    ----------
    src : str
        The source string to hash.

    Returns
    -------
    str
        MD5 hash as a hexadecimal string.

    Examples
    --------
    >>> hash_value = calculate_md5("Hello World")
    >>> print(len(hash_value))
    32
    """
    return hashlib.md5(src.encode("utf-8")).hexdigest()


def process_unicode(src, fname, tempdir):
    """
    Process Unicode characters in source content and save to temporary file.

    This function replaces specific Unicode characters with their LaTeX equivalents
    and writes the processed content to a temporary file.

    Parameters
    ----------
    src : str
        Source content to process.
    fname : str
        Original filename to use for the temporary file.
    tempdir : str
        Path to the temporary directory where the processed file will be saved.

    Returns
    -------
    str
        Path to the processed temporary file.

    Examples
    --------
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     processed_path = process_unicode("a ≠ b", "test.md", tmpdir)
    ...     with open(processed_path) as f:
    ...         print(f.read())
    a $\neq$ b
    """
    output = os.path.join(tempdir, fname)
    for pattern, replace in REPLACES.items():
        src = src.replace(pattern, replace)

    with open(output, "w", encoding="utf-8") as f:
        f.write(src)
    return output


def run_pandoc(path, output_path, ignore_error):
    """
    Execute Pandoc command to convert Markdown to PDF.

    Parameters
    ----------
    path : str
        Path to the input Markdown file.
    output_path : str
        Path where the output PDF should be saved.
    ignore_error : bool
        Whether to ignore Pandoc errors and continue execution.

    Returns
    -------
    sh.RunningCommand or None
        Pandoc command result if successful, None if error was ignored.

    Raises
    ------
    sh.ErrorReturnCode
        If Pandoc execution fails and ignore_error is False.

    Examples
    --------
    >>> run_pandoc("input.md", "output.pdf", ignore_error=True)
    """
    pandoc = PANDOC_CMD_TEMPLATE.bake(path, output=output_path)
    try:
        return pandoc()
    except sh.ErrorReturnCode as err:
        if ignore_error:
            print("=======================")
            print(">>> IGNORANDO ERROR <<<")
            print("=======================")
            print(err)
        else:
            raise err


def main():
    """
    Main function that orchestrates the Markdown to PDF compilation process.

    This function handles command line argument parsing, file monitoring,
    and coordinates the compilation process. It supports both single compilation
    and watch mode for continuous compilation on file changes.

    The function performs the following steps:
    1. Parse command line arguments
    2. Set up working directory and file paths
    3. Process the initial file and compile to PDF
    4. If in watch mode, monitor file for changes and recompile as needed

    Examples
    --------
    Run from command line:
    $ python script.py document.md --watch --sleep 2.0
    """
    parser = get_parser()

    args = parser.parse_args()
    sleep = args.sleep
    original_path = args.archivo
    watch = args.watch
    ignore_error = args.ignore_error
    cd = args.cd

    wd = sh.pwd()
    filepath = original_path
    if cd:
        wd = os.path.dirname(filepath)
        filepath = os.path.basename(filepath)

    output_path = filepath.replace(".md", ".pdf")

    with chdir(wd), tempfile.TemporaryDirectory() as tempdir:

        if watch:
            msg = f">>>>>> Watching every {sleep} seconds for changes in {original_path!r} <<<<<<"
            print("=" * len(msg))
            print(msg)
            print("=" * len(msg))

        src = read_file(filepath)
        md5 = calculate_md5(src)
        processed_path = process_unicode(src, filepath, tempdir)

        print("Proccesed file:", processed_path)
        print("Compiling", original_path, "-> ", os.path.join(wd, output_path))
        run_pandoc(processed_path, output_path, ignore_error)

        while watch:
            time.sleep(sleep)

            src = read_file(filepath)
            new_md5 = calculate_md5(src)

            if md5 != new_md5:
                print(
                    "Compiling",
                    original_path,
                    "-> ",
                    os.path.join(wd, output_path),
                )
                processed_path = process_unicode(src, filepath, tempdir)
                run_pandoc(processed_path, output_path, ignore_error)
                md5 = new_md5


if __name__ == "__main__":
    main()

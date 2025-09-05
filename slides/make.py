import os
import contextlib
import time
import hashlib
import argparse
import tempfile

import sh

PANDOC_CMD_TEMPLATE = sh.Command("pandoc").bake(
    t="beamer"
)

REPLACES = {
    "≠": r"$\neq$",
}


@contextlib.contextmanager
def chdir(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def get_parser():
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
    parser.add_argument(
        "-w", "--watch", help="watch mode", action="store_true", default=False
    )
    parser.add_argument(
        "-i", "--ignore_error", action="store_false", default=True
    )
    parser.add_argument(
        "--cd",
        help="cambiar al directorio del archivo",
        action="store_true",
        default=True,
    )
    return parser


def read_file(path):
    with open(path, "r") as f:
        return f.read()


def calculate_md5(src):
    return hashlib.md5(src.encode("utf-8")).hexdigest()


def process_unicode(src, fname, tempdir):
    output = os.path.join(tempdir, fname)
    for pattern, replace in REPLACES.items():
        src = src.replace(pattern, replace)

    with open(output, "w", encoding="utf-8") as f:
        f.write(src)
    return output


def run_pandoc(path, output_path, ignore_error):
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

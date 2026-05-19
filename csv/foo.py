#!/usr/bin/env python3
"""
Convert EUC-KR encoded CSV file(s) to UTF-8 encoding.

Usage:
    python euckr_to_utf8.py input.csv
    python euckr_to_utf8.py input.csv -o output.csv
    python euckr_to_utf8.py *.csv --suffix _utf8
    python euckr_to_utf8.py folder/ --recursive
"""

import argparse
import glob
import os
import sys


def convert_file(input_path: str, output_path: str, verbose: bool = True) -> bool:
    """
    Convert a single CSV file from EUC-KR to UTF-8.

    Returns True on success, False on failure.
    """
    try:
        with open(input_path, "r", encoding="euc-kr", errors="replace") as f:
            content = f.read()

        with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
            # utf-8-sig writes BOM so Excel opens it correctly as UTF-8
            f.write(content)

        if verbose:
            print(f"  ✓  {input_path}  →  {output_path}")
        return True

    except FileNotFoundError:
        print(f"  ✗  {input_path}: file not found", file=sys.stderr)
        return False
    except UnicodeDecodeError as e:
        print(f"  ✗  {input_path}: decode error — {e}", file=sys.stderr)
        return False
    except OSError as e:
        print(f"  ✗  {input_path}: {e}", file=sys.stderr)
        return False


def resolve_output_path(input_path: str, output: str | None, suffix: str) -> str:
    """Compute the output file path."""
    if output:
        return output

    base, ext = os.path.splitext(input_path)
    if not ext:
        ext = ".csv"
    return f"{base}{suffix}{ext}"


def collect_inputs(paths: list[str], recursive: bool) -> list[str]:
    """Expand globs and optionally recurse into directories."""
    files = []
    for path in paths:
        if os.path.isdir(path):
            pattern = "**/*.csv" if recursive else "*.csv"
            found = glob.glob(os.path.join(path, pattern), recursive=recursive)
            files.extend(sorted(found))
        elif "*" in path or "?" in path:
            files.extend(sorted(glob.glob(path)))
        else:
            files.append(path)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert EUC-KR CSV file(s) to UTF-8 (with BOM for Excel compatibility)."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        metavar="FILE_OR_DIR",
        help="Input CSV file(s) or directory.",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT",
        help="Output file path (only valid when converting a single file).",
    )
    parser.add_argument(
        "--suffix",
        default="_utf8",
        metavar="SUFFIX",
        help='Suffix appended before the extension when no -o is given (default: "_utf8"). '
             'Use --suffix "" to overwrite in-place.',
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Recurse into directories.",
    )
    parser.add_argument(
        "--no-bom",
        action="store_true",
        help="Write plain UTF-8 without BOM (default writes UTF-8 BOM for Excel).",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress per-file output.",
    )

    args = parser.parse_args()

    input_files = collect_inputs(args.inputs, args.recursive)

    if not input_files:
        print("No input files found.", file=sys.stderr)
        sys.exit(1)

    if args.output and len(input_files) > 1:
        print(
            "Error: -o/--output can only be used with a single input file.",
            file=sys.stderr,
        )
        sys.exit(1)

    encoding = "utf-8" if args.no_bom else "utf-8-sig"
    verbose = not args.quiet

    if verbose:
        print(f"Converting {len(input_files)} file(s)  [EUC-KR → UTF-8{'‑BOM' if not args.no_bom else ''}]\n")

    ok = err = 0
    for input_path in input_files:
        output_path = resolve_output_path(input_path, args.output, args.suffix)

        try:
            with open(input_path, "r", encoding="euc-kr", errors="replace") as f:
                content = f.read()
            with open(output_path, "w", encoding=encoding, newline="") as f:
                f.write(content)
            if verbose:
                print(f"  ✓  {input_path}  →  {output_path}")
            ok += 1
        except Exception as e:
            print(f"  ✗  {input_path}: {e}", file=sys.stderr)
            err += 1

    if verbose:
        print(f"\nDone: {ok} succeeded, {err} failed.")

    if err:
        sys.exit(1)


if __name__ == "__main__":
    main()
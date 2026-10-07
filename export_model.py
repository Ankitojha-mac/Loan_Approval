"""
export_model.py — helper script for packaging the Loan Approval Streamlit app
==============================================================================

What it does
------------
1. Exports dummy/placeholder model artifacts — ``model.pkl`` and
   ``scaler.pkl`` — by training the same fallback pipeline ``app.py`` uses
   (Logistic Regression + StandardScaler on synthetic data). Replace these two
   files with your REAL trained artifacts whenever they are available; the app
   detects them automatically.
2. Packages ``app.py``, ``requirements.txt``, ``export_model.py``,
   ``model.pkl`` and ``scaler.pkl`` into a downloadable ``streamlit_app.zip``
   archive using the standard-library ``zipfile`` module.

Usage
-----
    python export_model.py                # export artifacts + build the zip
    python export_model.py --artifacts-only
    python export_model.py --zip-only     # pkls must already exist
    python export_model.py --output my_bundle.zip
"""

from __future__ import annotations

import argparse
import os
import pickle
import zipfile

from app import MODEL_FILE, SCALER_FILE, build_fallback_artifacts

APP_FILES = ["app.py", "requirements.txt", "export_model.py"]
ZIP_NAME = "streamlit_app.zip"


def export_artifacts() -> tuple[str, str]:
    """Train the fallback pipeline and write dummy model.pkl / scaler.pkl."""
    model, scaler = build_fallback_artifacts()
    with open(MODEL_FILE, "wb") as fh:
        pickle.dump(model, fh)
    with open(SCALER_FILE, "wb") as fh:
        pickle.dump(scaler, fh)
    print(f"[export_model] wrote {MODEL_FILE} ({os.path.getsize(MODEL_FILE):,} bytes)")
    print(f"[export_model] wrote {SCALER_FILE} ({os.path.getsize(SCALER_FILE):,} bytes)")
    return MODEL_FILE, SCALER_FILE


def build_zip(zip_name: str = ZIP_NAME) -> str:
    """Pack app.py, requirements.txt, export_model.py + pkls into one zip."""
    members = APP_FILES + [MODEL_FILE, SCALER_FILE]
    missing = [m for m in members if not os.path.exists(m)]
    if missing:
        raise FileNotFoundError(
            f"Cannot build zip — missing files: {', '.join(missing)}. "
            "Run without --zip-only first to generate the dummy artifacts."
        )

    with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in members:
            zf.write(name, arcname=name)

    print(f"[export_model] created {zip_name} ({os.path.getsize(zip_name):,} bytes) containing:")
    with zipfile.ZipFile(zip_name, "r") as zf:
        for info in zf.infolist():
            print(f"    - {info.filename} ({info.file_size:,} bytes)")
    return zip_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Export model artifacts and zip the Streamlit app.")
    parser.add_argument("--artifacts-only", action="store_true", help="Only write model.pkl / scaler.pkl.")
    parser.add_argument("--zip-only", action="store_true", help="Only build the zip (artifacts must exist).")
    parser.add_argument("--output", default=ZIP_NAME, help=f"Zip file name (default: {ZIP_NAME}).")
    args = parser.parse_args()

    if args.artifacts_only and args.zip_only:
        parser.error("--artifacts-only and --zip-only are mutually exclusive.")

    if not args.zip_only:
        export_artifacts()
    if not args.artifacts_only:
        build_zip(args.output)


if __name__ == "__main__":
    main()

import shutil
from pathlib import Path


def ensure_directory(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def move_files(downloads: Path) -> None:
    targets = {
        (".jpg", ".jpeg"): downloads.parent / "images",
        (".csv", ".xlsx"): downloads.parent / "data",
        (".txt", ".doc", ".pdf"): downloads.parent / "docs",
        (".zip",): downloads.parent / "archive",
    }

    for extensions, destination in targets.items():
        ensure_directory(destination)

    for item in downloads.iterdir():
        if not item.is_file():
            continue

        suffix = item.suffix.lower()
        for extensions, destination in targets.items():
            if suffix in extensions:
                target_path = destination / item.name
                shutil.move(str(item), str(target_path))
                break


if __name__ == "__main__":
    downloads_folder = Path(r"C:\Users\wlsdu\Downloads")
    if not downloads_folder.exists():
        raise FileNotFoundError(f"Downloads folder not found: {downloads_folder}")

    move_files(downloads_folder)
    print("Files moved successfully.")

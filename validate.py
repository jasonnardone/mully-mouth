"""Validation script to check project setup and dependencies."""
import importlib
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def print_header(text: str) -> None:
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)


def check_python_version() -> bool:
    """Check Python version >= 3.11."""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 11:
        print("✓ Python version is compatible")
        return True
    else:
        print("✗ Python 3.11 or higher required")
        return False


def check_dependencies() -> bool:
    """Check required dependencies are installed."""
    print_header("Checking Dependencies")

    required_packages = [
        "anthropic",
        "elevenlabs",
        "cv2",
        "mss",
        "pygetwindow",
        "imagehash",
        "PIL",
        "yaml",
        "numpy",
    ]

    all_installed = True

    for package in required_packages:
        try:
            # Special case for opencv
            if package == "cv2":
                importlib.import_module("cv2")
            else:
                importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_installed = False

    if all_installed:
        print("\nAll dependencies installed")
    else:
        print("\nMissing dependencies. Run: pip install -r requirements.txt")

    return all_installed


def check_project_structure() -> bool:
    """Check required directories and files exist."""
    print_header("Checking Project Structure")

    required_paths = [
        "src/models",
        "src/services",
        "src/cli",
        "src/lib",
        "config",
        "data/personalities",
        "tests",
    ]

    required_files = [
        "src/__init__.py",
        "src/models/__init__.py",
        "src/services/__init__.py",
        "src/cli/__init__.py",
        "src/lib/__init__.py",
        "config/config.yaml.template",
        "requirements.txt",
        "pyproject.toml",
    ]

    all_exist = True

    print("Directories:")
    for path in required_paths:
        exists = Path(path).exists()
        status = "✓" if exists else "✗"
        print(f"{status} {path}")
        if not exists:
            all_exist = False

    print("\nFiles:")
    for file in required_files:
        exists = Path(file).exists()
        status = "✓" if exists else "✗"
        print(f"{status} {file}")
        if not exists:
            all_exist = False

    if all_exist:
        print("\nProject structure is valid")
    else:
        print("\nMissing required paths")

    return all_exist


def check_configuration() -> bool:
    """Check configuration file exists."""
    print_header("Checking Configuration")

    config_file = Path("config/config.yaml")

    if config_file.exists():
        print("✓ config/config.yaml exists")
        print("\nConfiguration is set up")
        return True
    else:
        print("✗ config/config.yaml not found")
        print("\nRun the setup wizard: python setup_wizard.py")
        print("Or copy template: cp config/config.yaml.template config/config.yaml")
        return False


def check_personalities() -> bool:
    """Check personality files exist."""
    print_header("Checking Personalities")

    personalities = ["neutral", "sarcastic", "encouraging"]
    all_exist = True

    for personality in personalities:
        file_path = Path(f"data/personalities/{personality}.yaml")
        exists = file_path.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {personality}.yaml")
        if not exists:
            all_exist = False

    if all_exist:
        print("\nAll personalities available")
    else:
        print("\nMissing personality files")

    return all_exist


def main() -> int:
    """Run validation checks."""
    print_header("Mully Mouth - Project Validation")

    print("This script validates your project setup and dependencies.")

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Configuration", check_configuration),
        ("Personalities", check_personalities),
    ]

    results = []

    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\nError during {name} check: {e}")
            results.append((name, False))

    # Summary
    print_header("Validation Summary")

    all_passed = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n✓ All checks passed! You're ready to use Mully Mouth.")
        print("\nTo get started:")
        print("  1. Launch GS Pro")
        print("  2. Run: python -m src.cli.main")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

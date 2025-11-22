"""Single instance enforcement for Mully Mouth."""
import os
import sys
import tempfile
from pathlib import Path


class SingleInstanceError(Exception):
    """Raised when another instance is already running."""
    pass


class SingleInstance:
    """
    Enforce single instance of the application using a lock file.

    Cross-platform implementation using file locking.
    """

    def __init__(self, app_name: str = "mully_mouth"):
        """
        Initialize single instance checker.

        Args:
            app_name: Application name for lock file

        Raises:
            SingleInstanceError: If another instance is already running
        """
        self.app_name = app_name
        self.lock_file = None
        self.fd = None

        # Create lock file path in temp directory
        temp_dir = Path(tempfile.gettempdir())
        self.lock_path = temp_dir / f"{app_name}.lock"

        # Try to acquire lock
        self._acquire_lock()

    def _acquire_lock(self) -> None:
        """
        Acquire lock file.

        Raises:
            SingleInstanceError: If another instance is already running
        """
        try:
            if sys.platform == 'win32':
                # Windows: Try to open file exclusively
                import msvcrt

                # Try to open/create lock file
                try:
                    # Open in exclusive mode - will fail if another process has it open
                    self.fd = os.open(
                        str(self.lock_path),
                        os.O_CREAT | os.O_EXCL | os.O_RDWR
                    )
                except FileExistsError:
                    # File exists - check if it's stale (old process)
                    try:
                        # Try to open for reading to check if locked
                        test_fd = os.open(str(self.lock_path), os.O_RDWR)

                        # Try to lock it
                        try:
                            msvcrt.locking(test_fd, msvcrt.LK_NBLCK, 1)
                            # Lock succeeded - old process is dead, we can use it
                            os.close(test_fd)
                            # Remove stale lock file
                            os.remove(str(self.lock_path))
                            # Try again
                            self.fd = os.open(
                                str(self.lock_path),
                                os.O_CREAT | os.O_EXCL | os.O_RDWR
                            )
                        except OSError:
                            # Lock failed - another instance is running
                            os.close(test_fd)
                            raise SingleInstanceError(
                                "Another instance of Mully Mouth is already running.\n\n"
                                "Please close the existing instance before starting a new one.\n"
                                "Check your system tray for the running instance."
                            )
                    except Exception:
                        raise SingleInstanceError(
                            "Another instance of Mully Mouth is already running.\n\n"
                            "Please close the existing instance before starting a new one.\n"
                            "Check your system tray for the running instance."
                        )

                # Lock the file
                msvcrt.locking(self.fd, msvcrt.LK_NBLCK, 1)

                # Write PID to file
                os.write(self.fd, str(os.getpid()).encode())

            else:
                # Unix/Linux/macOS: Use fcntl
                import fcntl

                # Open lock file
                self.lock_file = open(str(self.lock_path), 'w')

                # Try to acquire exclusive lock (non-blocking)
                try:
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    raise SingleInstanceError(
                        "Another instance of Mully Mouth is already running.\n\n"
                        "Please close the existing instance before starting a new one."
                    )

                # Write PID to file
                self.lock_file.write(str(os.getpid()))
                self.lock_file.flush()

        except SingleInstanceError:
            # Re-raise single instance errors
            raise
        except Exception as e:
            # Other errors - allow app to continue (fail-safe)
            print(f"Warning: Could not create lock file: {e}")

    def release(self) -> None:
        """Release the lock file."""
        try:
            if sys.platform == 'win32':
                if self.fd is not None:
                    import msvcrt
                    try:
                        # Unlock the file
                        msvcrt.locking(self.fd, msvcrt.LK_UNLCK, 1)
                    except:
                        pass
                    # Close file descriptor
                    os.close(self.fd)
                    self.fd = None
            else:
                if self.lock_file is not None:
                    import fcntl
                    try:
                        # Unlock
                        fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                    except:
                        pass
                    # Close file
                    self.lock_file.close()
                    self.lock_file = None

            # Remove lock file
            if self.lock_path.exists():
                try:
                    os.remove(str(self.lock_path))
                except:
                    pass

        except Exception:
            # Ignore errors during cleanup
            pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
        return False

    def __del__(self):
        """Destructor - ensure lock is released."""
        self.release()

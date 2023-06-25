"""Module contain atomic objects implementation"""
import threading


class AtomicInteger:
    """Integer which cannot be race conditional"""

    def __init__(self, value: int = 0):
        """Init Atomic Integer class

        Args:
            value (int, optional): value of Atomic Integer. Defaults to 0.
        """
        self._value = int(value)
        self._lock = threading.Lock()

    def inc(self, i: int = 1) -> int:
        """Increase atomic by a value, default is 1

        Args:
            i: (int) - the number which increase. Default = 1

        Returns:
            int - the value of atomic after increase
        """
        with self._lock:
            self._value += int(i)
            return self._value

    def dec(self, i: int = 1) -> int:
        """Decrease atomic by a value, default is 1

        Args:
            i: (int) - the number which decrease. Default = 1

        Returns:
            int: the value of atomic after decrease
        """
        return self.inc(-i)

    @property
    def value(self) -> int:
        """Value of Atomic

        Returns:
            int: _description_
        """
        with self._lock:
            return self._value

    @value.setter
    def value(self, value: int):
        with self._lock:
            self._value = int(value)

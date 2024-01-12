"""
Uses "duck typing" to mock a template interface for what a test class should look like
"""
import threading

from LSL import EventLogger


class TestThread(threading.Thread):
    def __init__(self, duration, test_gui, lsl):
        super().__init__()

        self.name = self.__class__.__name__

        self.duration = duration
        self.test_gui = test_gui
        self.lsl = lsl

        self._stop_event = threading.Event()

    def stop(self):
        """
        All logic related to destroying the test/any Tkinter widgets associated
        """
        EventLogger.record_timestamp(f"{self.name} End")
        self.lsl.stop_collection()

        self.test_gui.enable_buttons()

        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        """
        All logic related to the lifetime of the test
        """
        self.test_gui.disable_buttons(self.name)

        self.lsl.start_collection()  # Start LSL collection
        EventLogger.record_timestamp(f"{self.name} Start")

        # Schedule to stop the test after 15 seconds
        self.test_gui.display_window.after(self.duration, self.stop)

        return  # End thread

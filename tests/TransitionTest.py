import tkinter as tk

import config
from LSL import LSL
from tests.TestGUI import TestGUI
from tests.TestThread import TestThread


class TransitionTest(TestThread):
    """

    """

    def __init__(self, name, image_directory_1, image_directory_2):
        """
        Initializes and creates the transition labels in the display window.
        """
        super().__init__(name)

        self.image_1 = tk.PhotoImage(file=image_directory_1)
        self.image_2 = tk.PhotoImage(file=image_directory_2)

        self.label_1 = name.split(" to ")[0]
        self.label_2 = name.split(" to ")[1]

        self.firstImage = True
        self.current_image = None

    def run_test(self):
        """
        Main loop that runs and schedules the next iteration of the test
        """
        if self.iteration == config.ITERATIONS_PER_ACTION:
            self.running = False

        if self.running:
            if self.firstImage:
                LSL.start_label(self.label_1)
                self.current_image = TestGUI.place_image(self.image_1)
            else:
                LSL.start_label(self.label_2)
                self.current_image = TestGUI.place_image(self.image_2)

            self.playsound()

            def swap():
                self.firstImage = not self.firstImage
                self.run_test()

            self.test_job_id = TestGUI.display_window.after(config.TRANSITION_DURATION * 1000, swap)

            self.iteration += 1
        else:
            # Stop test thread
            self.running = False
            TestGUI.destroy_current_element()

            LSL.stop_label()
            self.stop()

import time
import tkinter as tk

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import config


class TestGUI:
    """
    Holds all logic relating to creating the GUI, adding buttons/windows, and the test confirmation window.
    """

    control_window = None
    display_window = None

    test_buttons = {}
    test_status = {}
    current_test = None

    @staticmethod
    def init_gui():
        """
        MUST BE CALLED BEFORE ACCESSING ANY CLASS VARIABLES. Sets up the display window.
        """
        TestGUI.control_window = tk.Tk()
        TestGUI.control_window.title("Control Panel")
        TestGUI.__set_window_geometry(TestGUI.control_window, left_side=True)

        TestGUI.display_window = tk.Toplevel(TestGUI.control_window)
        TestGUI.display_window.title("Display")
        TestGUI.__set_window_geometry(TestGUI.display_window, left_side=False)

    @staticmethod
    def add_button(test_name, test_lambda):
        """
        Adds a button to the test window with its name and function to run.
        """
        btn = tk.Button(TestGUI.control_window, text=test_name)
        btn.config(command=test_lambda, bg='red')
        btn.pack()
        TestGUI.test_buttons[test_name] = btn
        TestGUI.test_status[test_name] = False
        print("Added test: " + test_name)

    @staticmethod
    def confirm_test():
        """
        Run the test and prompt the user to confirm or deny the data
        """
        # TODO move this to LSL package for accurate labelling
        time.sleep(1)  # Wait one second until data collection is complete

        TestGUI.__show_data_and_confirm()  # TODO if denied, move to next test and allow for a rerun

    @staticmethod
    def disable_buttons(test_name):
        """
        A function to disable buttons while a test is running.
        """
        for button in TestGUI.test_buttons.values():
            button.config(state="disabled")

        TestGUI.current_test = test_name
        TestGUI.test_buttons[TestGUI.current_test].config(bg="yellow")

    #
    # HELPER METHODS
    #

    @staticmethod
    def __enable_buttons():
        """
        A function to enable buttons after a test has been completed.
        """
        # Reset the buttons
        for test in TestGUI.test_buttons.keys():
            if not TestGUI.test_status[test]:  # If test is not complete, re-enable button
                TestGUI.test_buttons[test].config(state="normal")

        TestGUI.current_test = None

    @staticmethod
    def __show_data_and_confirm():
        """
        Popup the data confirmation window and check if it should be accepted or rejected.
        TODO return boolean to determine whether to move onto a new test.
        """
        # Setup the window and canvas
        popup = tk.Toplevel()
        popup.wm_title("Data Confirmation")
        popup.wm_state('zoomed')

        canvas = tk.Canvas(popup)
        scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Make it scrollable so we don't have to click the tiny scrollbar
        TestGUI.__enable_scroll(canvas)

        data_df = pd.read_csv(config.COLLECTED_DATA_PATH)

        # Figure out how many graphs we can fit on the screen
        screen_width = popup.winfo_screenwidth()
        graphs_per_row = screen_width // config.WIDTH_PER_GRAPH

        if graphs_per_row == 0:
            graphs_per_row = 1

        # TODO do we want to draw the graphs from the timestamp of the past test?

        # Loop through each EEG and draw the graphs
        idx = 0
        for idx, col in enumerate(data_df.filter(like='EEG')):
            fig, ax = plt.subplots(figsize=(config.WIDTH_PER_GRAPH / config.HEIGHT_PER_GRAPH, 3))
            ax.plot(data_df[col])
            ax.set_title(f'{col} Data')
            FigureCanvasTkAgg(fig, master=scrollable_frame).get_tk_widget().grid(row=idx // graphs_per_row,
                                                                                 column=idx % graphs_per_row)

        # Now draw the accelerometer graph at the end
        accel_data = data_df.filter(like='Accelerometer').mean(axis=1)
        fig2, ax2 = plt.subplots(
            figsize=(config.WIDTH_PER_GRAPH / config.HEIGHT_PER_GRAPH, 3))
        ax2.plot(accel_data)
        ax2.set_title('Accelerometer Data')
        FigureCanvasTkAgg(fig2, master=scrollable_frame).get_tk_widget().grid(row=(idx + 1) // graphs_per_row,
                                                                              column=(idx + 1) % graphs_per_row)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create buttons to accept and deny the data
        confirm_button = tk.Button(scrollable_frame, text="Confirm Data", command=lambda: TestGUI.__confirm_data(popup))
        confirm_button.grid(row=(idx + 2) // graphs_per_row, column=0, pady=10)

        deny_button = tk.Button(scrollable_frame, text="Deny Data", command=lambda: TestGUI.__deny_data(popup))
        deny_button.grid(row=(idx + 2) // graphs_per_row, column=1, pady=10)

        # TODO explicitly destroy the graphs

        popup.mainloop()

    @staticmethod
    def __confirm_data(popup):
        """
        Run if the accept button is pressed

        :param popup: Popup window which must be closed
        """
        popup.destroy()

        # Set button color to green and disable to mark that the test has been completed
        TestGUI.test_buttons[TestGUI.current_test].config(bg="green")
        TestGUI.test_buttons[TestGUI.current_test].config(state="disabled")
        TestGUI.test_status[TestGUI.current_test] = True

        TestGUI.__enable_buttons()

        # TODO save test and mark as done

    @staticmethod
    def __deny_data(popup):
        """
        Run if the deny button is pressed

        :param popup: Popup window which must be closed
        """
        # Close window and then clear all the data
        popup.destroy()
        TestGUI.test_buttons[TestGUI.current_test].config(bg="red")
        TestGUI.__enable_buttons()

        # TODO if this is called, move to next test

    @staticmethod
    def __enable_scroll(canvas):
        """
        Function to enable scrolling using the mouse wheel

        NOTE: There may be a better solution for this, this is what I could find easily online
        """
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

    @staticmethod
    def __set_window_geometry(window, left_side=True):
        """
        Figure out size for a window and align it according to left_side

        :param window: Window passed from TKinter
        :param left_side: If it should be aligned on the left side or right
        """
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        if config.FULL_SCREEN_MODE:
            window.geometry(f"{screen_width}x{screen_height}+0+0")
        else:
            width = screen_width // 2
            x = 0 if left_side else width
            window.geometry(f"{width}x{screen_height}+{x}+0")

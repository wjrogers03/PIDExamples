class dprinter:
    def __init__(self, debug=False):
        """

        A debug printer that operates based on a debug variable. For handling non-interrupt debug logging.

        :param debug: bool
        """

        self.debug = debug

    def print(self, msg):
        """
        Print replacement method.

        :param msg: message to print
        """
        if self.debug:
            print(msg)

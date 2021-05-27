"""
RISC OS Screen information.

Creating object:

    # an object which operates on the current graphics output
    s = Screen()

    # an object which returns information for mode 28
    s = Screen(28)

    # an object which returns information for a mode by its mode string
    s = Screen("X800 Y600 C256")

Select a mode:

    s = Screen(28)
    s.select()

Get information:

    s = Screen()
    print("Screen is {} x {} and has {} colours".format(s.width, s.height, s.colours))
"""

import swi


# Constants for OS_ReadModeVariable/OS_ReadModeVariables
ModeVariable_ModeFlags = 0
ModeVariable_ScrRCol = 1
ModeVariable_ScrBRow = 2
ModeVariable_NColour = 3
ModeVariable_XEigFactor = 4
ModeVariable_YEigFactor = 5
ModeVariable_LineLength = 6
ModeVariable_ScreenSize = 7
ModeVariable_YShftFactor = 8
ModeVariable_Log2BPP = 9
ModeVariable_Log2BPC = 10
ModeVariable_XWindLimit = 11
ModeVariable_YWindLimit = 12

# Constants for OS_ScreenMode
ScreenModeReason_SelectMode = 0x0
ScreenModeReason_ReturnMode = 0x1
ScreenModeReason_EnumerateModes = 0x2
ScreenModeReason_SelectMonitorType = 0x3
ScreenModeReason_ChocolateConfigure = 0x4       # control chocolate flavour screen
ScreenModeReason_ChocolateUpdate = 0x5          # ensure chocolate flavour screen up to date, if not suspended
ScreenModeReason_ChocolateForceUpdate = 0x6     # force chocolate flavour screen up to date, even if suspended
ScreenModeReason_BankCount = 0x7                # read the number of screen banks
ScreenModeReason_BankDisplay = 0x8              # select/read the bank to show
ScreenModeReason_BankDriver = 0x9               # select/read the bank to write to
ScreenModeReason_BankCopy = 0xa                 # copy data between banks
ScreenModeReason_DisplaySelect = 0xb            # select a display driver
ScreenModeReason_DisplayDetails = 0xc           # details on the display
ScreenModeReason_DecodeModeString = 0xd         # parse a string into specifier
ScreenModeReason_EncodeModeString = 0xe         # generate a string from a specifier
ScreenModeReason_SelectModeString = 0xf         # select a mode given a mode string
ScreenModeReason_Limit = 0x10
ScreenModeReason_DisplayRegister = 0xff
ScreenModeReason_DisplayDeregister = 0xfe
ScreenModeReason_DisplayMax = 0xfd



def read_mode_variable(mode, varnum):
    value = swi.swi('OS_ReadModeVariable', 'ii;..I', mode, varnum)
    return value


class Screen(object):

    def __init__(self, mode=-1):
        self.mode = mode
        self.mode_specifier = None
        if isinstance(mode, str):
            self.mode_specifier = self.decode_mode_string(mode)
            self.mode = self.mode_specifier.start

    @staticmethod
    def decode_mode_string(mode_string):
        """
        Decode a mode string to a mode_specifier in a swi block
        """
        mode_specifier = swi.block(64)
        swi.swi('OS_ScreenMode', 'isbi', ScreenModeReason_DecodeModeString, mode_string,
                                         mode_specifier, mode_specifier.length)
        return mode_specifier

    def select(self):
        if self.mode == -1:
            mode = swi.swi('OS_ScreenMode', 'i;.i', ScreenModeReason_ReturnMode)
        else:
            mode = self.mode
        swi.swi('OS_ScreenMode', 'ii', ScreenModeReason_SelectMode, mode)

    def save(self, filename, palette=False):
        swi.swi('OS_SpriteOp', 'i.si', 2, filename, 1 if palette else 0)

    @property
    def text_width(self):
        return read_mode_variable(self.mode, ModeVariable_ScrRCol) + 1

    @property
    def text_height(self):
        return read_mode_variable(self.mode, ModeVariable_ScrBRow) + 1

    @property
    def colours(self):
        return read_mode_variable(self.mode, ModeVariable_NColour) + 1

    @property
    def xwindlimit(self):
        return read_mode_variable(self.mode, ModeVariable_XWindLimit)

    @property
    def ywindlimit(self):
        return read_mode_variable(self.mode, ModeVariable_YWindLimit)

    @property
    def xeigfactor(self):
        return read_mode_variable(self.mode, ModeVariable_XEigFactor)

    @property
    def yeigfactor(self):
        return read_mode_variable(self.mode, ModeVariable_YEigFactor)

    @property
    def width(self):
        return (self.xwindlimit + 1) << self.xeigfactor

    @property
    def height(self):
        return (self.ywindlimit + 1) << self.yeigfactor

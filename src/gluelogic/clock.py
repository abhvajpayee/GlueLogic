from myhdl import block, delay, instance
import inspect
from utils import functionStat

@block
def clockDriver(clk, DELAY = 5):
    functionStat(inspect.currentframe().f_code.co_name, __name__)
    """ Clock driver

    clk -- output signal, 50% duty cycle drived clock
    DELAY -- nano second delay for derived clock
    """
    @instance
    def clkgen():
        while(1):
            yield delay(DELAY)   
            clk.next = not clk
    return clkgen
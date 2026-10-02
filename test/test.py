import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

# Helper function to send a byte over UART
async def uart_send_byte(dut, data, clocks_per_bit):
    # 1. Send Start Bit (Drive RX low)
    dut.ui_in.value = 0 
    await ClockCycles(dut.clk, clocks_per_bit)

    # 2. Send 8 Data Bits (LSB first)
    for i in range(8):
        bit = (data >> i) & 1
        dut.ui_in.value = bit
        await ClockCycles(dut.clk, clocks_per_bit)

    # 3. Send Stop Bit (Drive RX high)
    dut.ui_in.value = 1 
    await ClockCycles(dut.clk, clocks_per_bit)

@cocotb.test()
async def test_uart_rx(dut):
    dut._log.info("Starting UART Test")

    # Start the clock (e.g., 50 MHz = 20ns period)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Calculate baud rate timing
    # e.g., 50MHz clock / 115200 baud = ~434 clocks per bit
    CLOCKS_PER_BIT = 434 

    # Reset the design
    dut.ena.value = 1
    dut.ui_in.value = 1 # RX idles high
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 10)

    dut._log.info("Sending the character 'A' (0x41)")
    
    # Send the byte 0x41 using our helper function
    await uart_send_byte(dut, 0x41, CLOCKS_PER_BIT)

    # Wait a bit for your UART to process the received byte
    await ClockCycles(dut.clk, 100)

    # Check if your module successfully parsed the byte internally
    # (Assuming you mapped the received byte to the uo_out pins for testing)
    assert dut.uo_out.value == 0x41, f"Expected 0x41, got {dut.uo_out.value}"

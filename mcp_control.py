import smbus
import time


MCP_ADDR = 0X20
IODIRA = 0X00
GPIOA = 0X12

bus = smbus.SMBus(1)

bus.write_byte_data(MCP_ADDR, IODIRA, 0XFF)

def leer_entrada():
    return bus.read_byte_data(MCP_ADDR, GPIOA)
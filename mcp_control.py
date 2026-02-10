import smbus

bus = smbus.SMBus(1)

MCP1 = 0x20
MCP2 = 0x21

IODIRA = 0x00
IODIRB = 0x01
GPIOA = 0x12
GPIOB = 0x13

# Configurar todos como salida
for addr in (MCP1, MCP2):
    bus.write_byte_data(addr, IODIRA, 0x00)
    bus.write_byte_data(addr, IODIRB, 0x00)

def activar_salida(num):
    if not 1 <= num <= 32:
        return

    # Apagar todo
    for addr in (MCP1, MCP2):
        bus.write_byte_data(addr, GPIOA, 0x00)
        bus.write_byte_data(addr, GPIOB, 0x00)

    if num <= 16:
        bus.write_byte_data(MCP1, GPIOA, 1 << (num - 1))
    else:
        bus.write_byte_data(MCP2, GPIOA, 1 << (num - 17))

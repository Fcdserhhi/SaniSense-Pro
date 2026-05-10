import time
from machine import I2C, Pin

_REG_IDENTIFICATION_MODEL_ID          = 0xC0
_REG_VHV_CONFIG_PAD_SCL_SDA_EXTSUP_HV = 0x89
_REG_MSRC_CONFIG_CONTROL              = 0x60
_REG_FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT = 0x44
_REG_SYSTEM_SEQUENCE_CONFIG           = 0x01
_REG_DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD = 0x4E
_REG_DYNAMIC_SPAD_REF_EN_START_OFFSET = 0x4F
_REG_GLOBAL_CONFIG_REF_EN_START_SELECT = 0xB6
_REG_SYSTEM_INTERRUPT_CONFIG_GPIO    = 0x0A
_REG_GPIO_HV_MUX_ACTIVE_HIGH         = 0x84
_REG_SYSTEM_INTERRUPT_CLEAR          = 0x0B
_REG_RESULT_INTERRUPT_STATUS         = 0x13
_REG_SYSRANGE_START                   = 0x00
_REG_RESULT_RANGE_STATUS              = 0x14
_REG_I2C_SLAVE_DEVICE_ADDRESS         = 0x8A
_REG_ALGO_PHASECAL_LIM                = 0x30
_REG_ALGO_PHASECAL_CONFIG_TIMEOUT     = 0x30


class VL53L0X:
    def __init__(self, i2c, address=0x29):
        self.i2c = i2c
        self.address = address
        self._init_sensor()

    def _write_byte(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def _read_byte(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def _read_word(self, reg):
        data = self.i2c.readfrom_mem(self.address, reg, 2)
        return (data[0] << 8) | data[1]

    def _write_word(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([(value >> 8) & 0xFF, value & 0xFF]))

    def _init_sensor(self):
        model_id = self._read_byte(_REG_IDENTIFICATION_MODEL_ID)
        if model_id != 0xEE:
            raise RuntimeError(f"VL53L0X not found! Got model ID: {hex(model_id)}")

        self._write_byte(0x88, 0x00)
        self._write_byte(0x80, 0x01)
        self._write_byte(0xFF, 0x01)
        self._write_byte(0x00, 0x00)
        self._stop_variable = self._read_byte(0x91)
        self._write_byte(0x00, 0x01)
        self._write_byte(0xFF, 0x00)
        self._write_byte(0x80, 0x00)

        config_control = self._read_byte(_REG_MSRC_CONFIG_CONTROL)
        self._write_byte(_REG_MSRC_CONFIG_CONTROL, config_control | 0x12)

        self._write_word(_REG_FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT, 32)

        self._write_byte(_REG_SYSTEM_SEQUENCE_CONFIG, 0xFF)

        self._spad_init()

        self._load_tuning_settings()

        self._write_byte(_REG_SYSTEM_INTERRUPT_CONFIG_GPIO, 0x04)
        gpio_hv_mux = self._read_byte(_REG_GPIO_HV_MUX_ACTIVE_HIGH)
        self._write_byte(_REG_GPIO_HV_MUX_ACTIVE_HIGH, gpio_hv_mux & ~0x10)
        self._write_byte(_REG_SYSTEM_INTERRUPT_CLEAR, 0x01)

        self._write_byte(_REG_SYSTEM_SEQUENCE_CONFIG, 0xE8)

        self._write_byte(_REG_SYSTEM_SEQUENCE_CONFIG, 0x01)
        self._perform_single_ref_calibration(0x40)
        self._write_byte(_REG_SYSTEM_SEQUENCE_CONFIG, 0x02)
        self._perform_single_ref_calibration(0x00)

        self._write_byte(_REG_SYSTEM_SEQUENCE_CONFIG, 0xE8)

    def _spad_init(self):
        self._write_byte(0x80, 0x01)
        self._write_byte(0xFF, 0x01)
        self._write_byte(0x00, 0x00)
        self._write_byte(0xFF, 0x06)
        val = self._read_byte(0x83)
        self._write_byte(0x83, val | 0x04)
        self._write_byte(0xFF, 0x07)
        self._write_byte(0x81, 0x01)
        self._write_byte(0x80, 0x01)
        self._write_byte(0x94, 0x6B)
        self._write_byte(0x83, 0x00)

        timeout = 0
        while self._read_byte(0x83) == 0x00:
            time.sleep_ms(1)
            timeout += 1
            if timeout > 500:
                raise RuntimeError("VL53L0X SPAD init timeout")

        self._write_byte(0x83, 0x01)
        tmp = self._read_byte(0x92)
        spad_count = tmp & 0x7F
        spad_type_is_aperture = (tmp >> 7) & 0x01

        self._write_byte(0x81, 0x00)
        self._write_byte(0xFF, 0x06)
        val = self._read_byte(0x83)
        self._write_byte(0x83, val & ~0x04)
        self._write_byte(0xFF, 0x01)
        self._write_byte(0x00, 0x01)
        self._write_byte(0xFF, 0x00)
        self._write_byte(0x80, 0x00)

        ref_spad_map = bytearray(self.i2c.readfrom_mem(self.address, _REG_GLOBAL_CONFIG_REF_EN_START_SELECT, 6))
        self._write_byte(_REG_DYNAMIC_SPAD_REF_EN_START_OFFSET, 0x00)
        self._write_byte(_REG_DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD, 0x2C)
        self._write_byte(_REG_GLOBAL_CONFIG_REF_EN_START_SELECT, 0xB4)

        first_spad_to_enable = 12 if spad_type_is_aperture else 0
        spads_enabled = 0

        for i in range(48):
            if i < first_spad_to_enable or spads_enabled == spad_count:
                ref_spad_map[i // 8] &= ~(1 << (i % 8))
            elif (ref_spad_map[i // 8] >> (i % 8)) & 0x01:
                spads_enabled += 1

        self.i2c.writeto_mem(self.address, _REG_GLOBAL_CONFIG_REF_EN_START_SELECT, ref_spad_map)

    def _load_tuning_settings(self):
        settings = [
            (0xFF, 0x01), (0x00, 0x00), (0xFF, 0x00), (0x09, 0x00),
            (0x10, 0x00), (0x11, 0x00), (0x24, 0x01), (0x25, 0xFF),
            (0x75, 0x00), (0xFF, 0x01), (0x4E, 0x2C), (0x48, 0x00),
            (0x30, 0x20), (0xFF, 0x00), (0x30, 0x09), (0x54, 0x00),
            (0x31, 0x04), (0x32, 0x03), (0x40, 0x83), (0x46, 0x25),
            (0x60, 0x00), (0x27, 0x00), (0x50, 0x06), (0x51, 0x00),
            (0x52, 0x96), (0x56, 0x08), (0x57, 0x30), (0x61, 0x00),
            (0x62, 0x00), (0x64, 0x00), (0x65, 0x00), (0x66, 0xA0),
            (0xFF, 0x01), (0x22, 0x32), (0x47, 0x14), (0x49, 0xFF),
            (0x4A, 0x00), (0xFF, 0x00), (0x7A, 0x0A), (0x7B, 0x00),
            (0x78, 0x21), (0xFF, 0x01), (0x23, 0x34), (0x42, 0x00),
            (0x44, 0xFF), (0x45, 0x26), (0x46, 0x05), (0x40, 0x40),
            (0x0E, 0x06), (0x20, 0x1A), (0x43, 0x40), (0xFF, 0x00),
            (0x34, 0x03), (0x35, 0x44), (0xFF, 0x01), (0x31, 0x04),
            (0x4B, 0x09), (0x4C, 0x05), (0x4D, 0x04), (0xFF, 0x00),
            (0x44, 0x00), (0x45, 0x20), (0x47, 0x08), (0x48, 0x28),
            (0x67, 0x00), (0x70, 0x04), (0x71, 0x01), (0x72, 0xFE),
            (0x76, 0x00), (0x77, 0x00), (0xFF, 0x01), (0x0D, 0x01),
            (0xFF, 0x00), (0x80, 0x01), (0x01, 0xF8), (0xFF, 0x01),
            (0x8E, 0x01), (0x00, 0x01), (0xFF, 0x00), (0x80, 0x00),
        ]
        for reg, val in settings:
            self._write_byte(reg, val)

    def _perform_single_ref_calibration(self, vhv_init_byte):
        self._write_byte(_REG_SYSRANGE_START, 0x01 | vhv_init_byte)
        timeout = 0
        while (self._read_byte(_REG_RESULT_INTERRUPT_STATUS) & 0x07) == 0:
            time.sleep_ms(1)
            timeout += 1
            if timeout > 500:
                raise RuntimeError("VL53L0X calibration timeout")
        self._write_byte(_REG_SYSTEM_INTERRUPT_CLEAR, 0x01)
        self._write_byte(_REG_SYSRANGE_START, 0x00)

    def read(self):
        self._write_byte(0x80, 0x01)
        self._write_byte(0xFF, 0x01)
        self._write_byte(0x00, 0x00)
        self._write_byte(0x91, self._stop_variable)
        self._write_byte(0x00, 0x01)
        self._write_byte(0xFF, 0x00)
        self._write_byte(0x80, 0x00)

        self._write_byte(_REG_SYSRANGE_START, 0x01)

        timeout = 0
        while self._read_byte(_REG_SYSRANGE_START) & 0x01:
            time.sleep_ms(1)
            timeout += 1
            if timeout > 500:
                raise RuntimeError("VL53L0X start timeout")

        timeout = 0
        while (self._read_byte(_REG_RESULT_INTERRUPT_STATUS) & 0x07) == 0:
            time.sleep_ms(1)
            timeout += 1
            if timeout > 500:
                raise RuntimeError("VL53L0X measurement timeout")

        range_mm = self._read_word(_REG_RESULT_RANGE_STATUS + 10)

        self._write_byte(_REG_SYSTEM_INTERRUPT_CLEAR, 0x01)

        if range_mm >= 8190:
            return None

        return range_mm

    def change_address(self, new_address):
        self._write_byte(_REG_I2C_SLAVE_DEVICE_ADDRESS, new_address & 0x7F)
        self.address = new_address

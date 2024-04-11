from conftest import wait
from conftest import SensorInfo
from time import sleep
import logging

log = logging.getLogger(__name__)


def test_sanity(get_sensor_info, get_sensor_reading):
    sensor_info = get_sensor_info()

    sensor_name = sensor_info.name
    assert isinstance(sensor_name, str), "Sensor name is not a string"

    sensor_hid = sensor_info.hid
    assert isinstance(sensor_hid, str), "Sensor hid is not a string"

    sensor_model = sensor_info.model
    assert isinstance(sensor_model, str), "Sensor model is not a string"

    sensor_firmware_version = sensor_info.firmware_version
    assert isinstance(
        sensor_firmware_version, int
    ), "Sensor firmware version is not a int"

    sensor_reading_interval = sensor_info.reading_interval
    assert isinstance(
        sensor_reading_interval, int
    ), "Sensor reading interval is not a string"

    sensor_reading = get_sensor_reading()
    assert isinstance(
        sensor_reading, float
    ), "Sensor doesn't seem to register temperature"

    print("Sanity test passed")


def test_reboot(get_sensor_info, reboot_sensor):
    
    log.info("Get original sensor info")
    sensor_info_before_reboot = get_sensor_info()

    log.info("Reboot sensor")
    reboot_response = reboot_sensor()
    assert (
        reboot_response == "rebooting"
    ), "Sensor didn't return proper text in response to reboot request"

    log.info("Wait for sensor to come back online")
    sensor_info_after_reboot = wait(
        func=get_sensor_info,
        condition=lambda x: isinstance(x, SensorInfo),
        tries=10,
        timeout=1,
    )

    log.info("Validate info from step1 is equal to info from step4")
    assert (
        sensor_info_before_reboot == sensor_info_after_reboot
    ), "Sensor info after reboot doesn't match sensor info before reboot"


def test_set_sensor_name(get_sensor_info, set_sensor_name):
    new_name = "new_name"
    log.info(f"Set sensor name to {new_name}")
    set_sensor_name(new_name)

    log.info("Get sensor info")
    sensor_info = get_sensor_info()

    log.info("Validate that current sensor name matches the name set in Step 1")
    assert sensor_info.name == new_name, f"Sensor name is not set to '{new_name}'"

    
def test_set_empty_sensor_name(get_sensor_info, set_sensor_name):
    log.info("Get original sensor name")
    original_sensor_name = get_sensor_info().name
    empty_name = ""
    log.info("Set sensor name to an empty string")
    set_sensor_name(empty_name)
    sensor_info = get_sensor_info()
    log.info("Validate that sensor responds with an error")
    assert sensor_info.name == original_sensor_name, "Sensor responded with unexpected name"

    log.info("Get current sensor name")
    current_sensor_name = sensor_info.name
    log.info("Validate that sensor name didn't change")
    assert current_sensor_name == original_sensor_name


def test_set_sensor_reading_interval(
    get_sensor_info, set_sensor_reading_interval, get_sensor_reading
):
    reading_interval = 1

    log.info("Set sensor reading interval to 1")
    sensor_info = set_sensor_reading_interval(reading_interval)

    log.info("Validate that sensor reading interval is set to interval from Step 1")
    assert sensor_info["reading_interval"] == reading_interval

    log.info("Get sensor reading")
    initial_reading = get_sensor_reading()

    log.info("Wait for interval specified in Step 1")
    sleep(reading_interval)
    
    log.info("Get sensor reading")
    final_reading = get_sensor_info()
    
    log.info("Validate that reading from Step 4 doesn't equal reading from Step 6")
    assert (
        initial_reading != final_reading
    ), "Sensor reading did not change after waiting for specified interval"



def test_set_invalid_sensor_reading_interval(get_sensor_info, set_sensor_reading_interval):

    log.info("Get original sensor reading interval")
    invalid_interval = -1
    log.info("Request reading interval update to invalid interval")
    set_sensor_reading_interval(invalid_interval)
    log.info("Check that sensor responds with an error")
    sensor_info = get_sensor_info()
    


def test_update_sensor_firmware(get_sensor_info, update_sensor_firmware):

    log.info("Get original sensor firmware version")
    original_firmware_version = get_sensor_info().firmware_version
    max_firmware_version = 15

    log.info("Request firmware update up until sensor version is 15")
    while original_firmware_version < max_firmware_version:
        update_sensor_firmware()
        current_firmware_version = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance(x, SensorInfo),
            tries=15,
            timeout=1,
        ).firmware_version

        log.info("Check that the version increased by 1 in each loop iteration")
        assert current_firmware_version == original_firmware_version + 1
        original_firmware_version += 1

    log.info("Request another firmware update")
    update_response = update_sensor_firmware()

    log.info("Validate that sensor is already at max version")
    assert update_response == "already at latest firmware version"

    log.info("Validate that sensor is still at max version")
    assert get_sensor_info().firmware_version == max_firmware_version
    

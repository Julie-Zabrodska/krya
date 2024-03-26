from conftest import wait
from time import sleep


def test_sanity(get_sensor_info, get_sensor_reading):
    sensor_info = get_sensor_info()

    sensor_name = sensor_info.get("name")
    assert isinstance(sensor_name, str), "Sensor name is not a string"

    sensor_hid = sensor_info.get("hid")
    assert isinstance(sensor_hid, str), "Sensor hid is not a string"

    sensor_model = sensor_info.get("model")
    assert isinstance(sensor_model, str), "Sensor model is not a string"

    sensor_firmware_version = sensor_info.get("firmware_version")
    assert isinstance(
        sensor_firmware_version, int
    ), "Sensor firmware version is not a int"

    sensor_reading_interval = sensor_info.get("reading_interval")
    assert isinstance(
        sensor_reading_interval, int
    ), "Sensor reading interval is not a string"

    sensor_reading = get_sensor_reading()
    assert isinstance(
        sensor_reading, float
    ), "Sensor doesn't seem to register temperature"

    print("Sanity test passed")


def test_reboot(get_sensor_info, reboot_sensor):
    """
    Steps:
        1. Get original sensor info
        2. Reboot sensor
        3. Wait for sensor to come back online
        4. Get current sensor info
        5. Validate that info from step 1 is equal to info from step 4
    """
    print("Get original sensor info")
    sensor_info_before_reboot = get_sensor_info()

    print("Reboot sensor")
    reboot_response = reboot_sensor()
    assert (
        reboot_response == "rebooting"
    ), "Sensor didn't return proper text in response to reboot request"

    print("Wait for sensor to come back online")
    sensor_info_after_reboot = wait(
        func=get_sensor_info,
        condition=lambda x: isinstance(x, dict),
        tries=10,
        timeout=1,
    )

    print("Validate info from step1 is equal to info from step4")
    assert (
        sensor_info_before_reboot == sensor_info_after_reboot
    ), "Sensor info after reboot doesn't match sensor info before reboot"


def test_set_sensor_name(get_sensor_info, set_sensor_name):
    """
    1. Set sensor name to "new_name"
    2. Get sensor_info
    3. Validate that current sensor name matches the name set in Step 1
    """
    new_name = "new_name"
    set_sensor_name(new_name)
    sensor_info = get_sensor_info()
    assert sensor_info["name"] == new_name, f"Sensor name is not set to '{new_name}'"


def test_set_sensor_reading_interval(
    get_sensor_info, set_reading_interval, get_sensor_reading
):
    """
    1. Set sensor reading interval to 1.
    2. Get sensor info.
    3. Validate that sensor reading interval is set to interval from Step 1.
    4. Get sensor reading.
    5. Wait for interval specified in Step 1.
    6. Get sensor reading.
    7. Validate that reading from Step 4 doesn't equal reading from Step 6.
    """
    reading_interval = 1
    set_reading_interval(reading_interval)
    sensor_info = get_sensor_info()
    assert sensor_info["reading_interval"] == reading_interval

    initial_reading = get_sensor_reading()
    sleep(reading_interval)
    final_reading = get_sensor_info()
    assert (
        initial_reading != final_reading
    ), "Sensor reading did not change after waiting for specified interval"


# Максимальна версія прошивки сенсора -- 15
def test_update_sensor_firmware(get_sensor_info, update_firmware):
    """
    1. Get original sensor firmware version.
    2. Request firmware update.
    3. Get current sensor firmware version.
    4. Validate that current firmware version is +1 to original firmware version.
    5. Repeat steps 1-4 until sensor is at max_firmware_version - 1.
    6. Update sensor to max firmware version.
    7. Validate that sensor is at max firmware version.
    8. Request another firmware update.
    9. Validate that sensor doesn't update and responds appropriately.
    10. Validate that sensor firmware version doesn't change if it's at maximum value.
    """

    original_firmware_version = get_sensor_info()["firmware_version"]

    update_firmware("new_version")
    current_firmware_version = wait(
        func=get_sensor_info,
        condition=lambda x: isinstance(x, dict),
        tries=10,
        timeout=3,
    )

    assert current_firmware_version["firmware_version"] == original_firmware_version + 1

    max_firmware_version = 15
    while current_firmware_version["firmware_version"] < max_firmware_version - 1:
        update_firmware("new_version")
        current_firmware_version = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance(x, dict),
            tries=10,
            timeout=3,
        )

    assert current_firmware_version["firmware_version"] == max_firmware_version - 1

    update_firmware(max_firmware_version)
    current_firmware_version = wait(
        func=get_sensor_info,
        condition=lambda x: isinstance(x, dict),
        tries=10,
        timeout=3,
    )
    assert current_firmware_version["firmware_version"] == max_firmware_version

    update_response = update_firmware("new_version")
    assert update_response == "already at latest firmware version"

    assert get_sensor_info()["firmware_version"] == max_firmware_version

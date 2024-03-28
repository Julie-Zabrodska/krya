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
    new_name = "new_name"
    set_sensor_name(new_name)
    sensor_info = get_sensor_info()
    assert sensor_info["name"] == new_name, f"Sensor name is not set to '{new_name}'"


def test_set_sensor_reading_interval(
    get_sensor_info, set_reading_interval, get_sensor_reading
):
    reading_interval = 1
    sensor_info = set_reading_interval(reading_interval)
    assert sensor_info["reading_interval"] == reading_interval

    initial_reading = get_sensor_reading()
    sleep(reading_interval)
    final_reading = get_sensor_info()
    assert (
        initial_reading != final_reading
    ), "Sensor reading did not change after waiting for specified interval"


def test_update_sensor_firmware(get_sensor_info, update_firmware):

    original_firmware_version = get_sensor_info()["firmware_version"]
    max_firmware_version = 15

    while original_firmware_version < max_firmware_version:
        update_firmware()
        current_firmware_version = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance(x, dict),
            tries=15,
            timeout=1,
        ).get("firmware_version")

        assert current_firmware_version == original_firmware_version + 1
        original_firmware_version += 1

    update_response = update_firmware()
    assert update_response == "already at latest firmware version"
    assert get_sensor_info()["firmware_version"] == max_firmware_version

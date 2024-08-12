import unittest
from unittest.mock import patch
import can

from canbus import (reader_loop, write_on_bus_all_rpm, write_on_bus_test,
                   write_on_bus_take_status, write_on_bus_take_rpm,
                   write_on_bus_all_config, write_scan_boards,
                   write_on_bus_rename, write_on_bus_factory_reset, Ids,
                   CanPortConfig, BoardParams, BoardTest, NodeConfiguration)

class TestCanBus(unittest.TestCase):
    @patch('can.interface.Bus')
    def test_reader_loop(self, mock_bus):
        bus_config = CanPortConfig(interface="socketcan", channel="can0", baudrate=250000)

        reader_loop(bus_config)

        mock_bus.assert_called_once_with(channel=bus_config.channel, interface=bus_config.interface, bitrate=bus_config.baudrate, receive_own_messages=True)

    @patch('can.interface.Bus')
    def test_write_on_bus_all_rpm(self, mock_bus):
        bus_config = CanPortConfig(interface="socketcan", channel="can0", baudrate=250000)
        params = BoardParams(1, 1000, 1000, 1000, 1000)

        write_on_bus_all_rpm(bus_config, params)

        mock_bus.assert_called_once_with(channel=bus_config.channel, interface=bus_config.interface, bitrate=bus_config.baudrate, receive_own_messages=True)
        mock_bus().send.assert_called_once_with(can.Message(arbitration_id=Ids.set_individual_rpm, data=[params.board_id_bytes[0], params.board_id_bytes[1], params.m1_rpm//50, params.m2_rpm//50, params.m3_rpm//50, params.m4_rpm//50, 0, 0], is_extended_id=True))

    @patch('can.interface.Bus')
    def test_write_on_bus_test(self, mock_bus):
        bus_config = CanPortConfig(interface="socketcan", channel="can0", baudrate=250000)
        params = BoardTest(1)

        write_on_bus_test(bus_config, params)

        mock_bus.assert_called_once_with(channel=bus_config.channel, interface=bus_config.interface, bitrate=bus_config.baudrate, receive_own_messages=True)
        mock_bus().send.assert_called_once_with(can.Message(arbitration_id=Ids.test_board, data=[params.board_id_bytes[0], params.board_id_bytes[1], 0, 0, 0, 0, 0, 0], is_extended_id=True))

    @patch('can.interface.Bus')
    def test_write_on_bus_take_status(self, mock_bus):
        bus_config = CanPortConfig(interface="socketcan", channel="can0", baudrate=250000)
        params = BoardTest(1)

        write_on_bus_take_status(bus_config, params)

        mock_bus.assert_called_once_with(channel=bus_config.channel, interface=bus_config.interface, bitrate=bus_config.baudrate, receive_own_messages=True)
        mock_bus().send.assert_called_once_with(can.Message(arbitration_id=Ids.take_test_response, data=[params.board_id_bytes[0], params.board_id_bytes[1], 0, 0, 0, 0, 0, 0], is_extended_id=True))

    @patch('can.interface.Bus')
    def test_write_on_bus_take_rpm(self, mock_bus):
        bus_config = CanPortConfig(interface="socketcan", channel="can0", baudrate=250000)
        params = BoardTest(1)

        write_on_bus_take_rpm(bus_config, params)

        mock_bus.assert_called_once_with(channel=bus_config.channel, interface=bus_config.interface, bitrate=bus_config.baudrate, receive_own_messages=True)
        mock_bus().send.assert_called_once_with(can.Message(arbitration_id=Ids.take_board_rpm, data=[params.board_id_bytes[0], params.board_id_bytes[1], 0, 0, 0, 0, 0, 0], is_extended_id=True))

    @patch('can.interface.Bus')
    def test_write_on_bus_all_config(self, mock_bus):
        bus_config = CanPortConfig(interface="socketcan", channel="can0", baudrate=250000)
        node = NodeConfiguration(1, 1.0, 1.0, 1.0, 1.0, 1, 1)

        write_on_bus_all_config(bus_config, node)

        mock_bus.assert_called_once_with(channel=bus_config.channel, interface=bus_config.interface, bitrate=bus_config.baudrate, receive_own_messages=True)
        mock_bus().send.assert_has_calls([
            call(can.Message(arbitration_id=Ids.config_rpm_variation, data=[node.board_id_bytes[0], node.board_id_bytes[1], int(node.variacion_rpm*10), 0, 0, 0, 0, 0], is_extended_id=True)),
            call(can.Message(arbitration_id=Ids.config_under_currency, data=[node.board_id_bytes[0], node.board_id_bytes[1], int(node.subcorriente*10), 0, 0, 0, 0, 0], is_extended_id=True)),
            call(can.Message(arbitration_id=Ids.config_over_currency, data=[node.board_id_bytes[0], node.board_id_bytes[1], int(node.sobrecorriente*10), 0, 0, 0, 0, 0], is_extended_id=True)),
            call(can.Message(arbitration_id=Ids.config_shortage, data=[node.board_id_bytes[0], node.board_id_bytes[1], int(node.cortocicuito*10), 0, 0, 0, 0, 0], is_extended_id=True)),
            call(can.Message(arbitration_id=Ids.config_sensor, data=[node.board_id_bytes[0], node.board_id_bytes[1], node.sensor, 0, 0, 0, 0, 0], is_extended_id=True)),
            call(can.Message(arbitration_id=Ids.config_valve, data=[node.board_id_bytes[0], node.board_id_bytes[1], node.electrovalvula, 0, 0, 0, 0, 0], is_extended_id=True))
        ])

    @patch('can.interface.Bus')
    def test_write_scan_boards(self, mock_bus):
        bus_config = CanPortConfig(interface="socketcan", channel="can0", baudrate=250000)

        write_scan_boards(bus_config)

        mock_bus.assert_called_once_with(channel=bus_config.channel, interface=bus_config.interface, bitrate=bus_config.baudrate, receive_own_messages=True)
        mock_bus().send.assert_called_once_with(can.Message(arbitration_id=Ids.ask_scan, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=True))

    @patch('can.interface.Bus')
    def test_write_on_bus_rename(self, mock_bus):
        bus_config = CanPortConfig(interface="socketcan", channel="can0", baudrate=250000)
        b1 = BoardTest(1)
        b2 = BoardTest(2)

        write_on_bus_rename(bus_config, b1, b2)

        mock_bus.assert_called_once_with(channel=bus_config.channel, interface=bus_config.interface, bitrate=bus_config.baudrate, receive_own_messages=True)
        mock_bus().send.assert_called_once_with(can.Message(arbitration_id=Ids.rename, data=[b1.board_id_bytes[0], b1.board_id_bytes[1], b2.board_id_bytes[0], b2.board_id_bytes[1], 0, 0, 0, 0], is_extended_id=True))

    @patch('can.interface.Bus')
    def test_write_on_bus_factory_reset(self, mock_bus):
        bus_config = CanPortConfig(interface="socketcan", channel="can0", baudrate=250000)
        params = BoardTest(1)

        write_on_bus_factory_reset(bus_config, params)

        mock_bus.assert_called_once_with(channel=bus_config.channel, interface=bus_config.interface, bitrate=bus_config.baudrate, receive_own_messages=True)
        mock_bus().send.assert_called_once_with(can.Message(arbitration_id=Ids.factory_reset, data=[params.board_id_bytes[0], params.board_id_bytes[1], 0, 0, 0, 0, 0, 0], is_extended_id=True))

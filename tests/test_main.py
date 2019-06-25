from unittest import mock
import os

from galaxy_swift.__main__ import main


@mock.patch(
    'os.getcwd',
    lambda: (
        os.path.dirname(os.path.abspath(__file__)) +
        '/data/dummy'
    ),
)
class TestDummyPlugin:

    prog_name = 'galaxy'

    def test_info(self, capfd):
        """Test info plugin"""
        args = ["info", ]
        main(args=args)

        out, err = capfd.readouterr()
        assert out == (
            "Info: \n"
            " Name: Example plugin\n"
            " Platform: generic\n"
            " Guid: UNIQUE-GUID\n"
            " Version: 0.1\n"
            " Description: Example plugin\n"
            " Author: Name\n"
            " Email: author@email.com\n"
            " Url: https://github.com/p1c2u/galaxy-plugin-example\n"
            " Script: plugin.py\n"
        )
        assert err == ""

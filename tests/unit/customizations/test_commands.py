# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from awscli.testutils import unittest
import mock

from awscli.customizations.commands import BasicHelp, BasicCommand


class MockCustomCommand(BasicCommand):
        NAME = 'mock'

        SUBCOMMANDS = [{'name': 'basic', 'command_class': BasicCommand}]


class TestCommandLoader(unittest.TestCase):

    def test_basic_help_with_contents(self):
        cmd_object = mock.Mock()
        mock_module = mock.Mock()
        mock_module.__file__ = '/some/root'
        cmd_object.DESCRIPTION = BasicCommand.FROM_FILE(
            'foo', 'bar', 'baz.txt', root_module=mock_module)
        help_command = BasicHelp(mock.Mock(), cmd_object, {}, {})
        with mock.patch('awscli.customizations.commands._open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = \
                    'fake description'
            self.assertEqual(help_command.description, 'fake description')


class TestBasicCommand(unittest.TestCase):
    def setUp(self):
        self.session = mock.Mock()
        self.command = BasicCommand(self.session)

    def test_load_arg_table_property(self):
        # Ensure ``_build_arg_table()`` is called if it has not been
        # built via the ``arg_table`` property.  It should be an empty
        # dictionary.
        orig_arg_table = self.command.arg_table
        self.assertEqual(orig_arg_table, {})
        # Ensure the ``arg_table`` is not built again if
        # ``arg_table`` property is called again.
        self.assertIs(orig_arg_table, self.command.arg_table)

    def test_load_subcommand_table_property(self):
        # Ensure ``_build_subcommand_table()`` is called if it has not
        # been built via the ``subcommand_table`` property. It should be
        # an empty dictionary.
        orig_subcommand_table = self.command.subcommand_table
        self.assertEqual(orig_subcommand_table, {})
        # Ensure the ``subcommand_table`` is not built again if
        # ``subcommand_table`` property is called again.
        self.assertIs(orig_subcommand_table, self.command.subcommand_table)

    def test_load_lineage(self):
        self.assertEqual(self.command.lineage, [self.command])
        self.assertEqual(self.command.lineage_names, [self.command.name])

    def test_pass_lineage_to_child_command(self):
        self.command = MockCustomCommand(self.session)
        subcommand = self.command.subcommand_table['basic']
        lineage = subcommand.lineage
        self.assertEqual(len(lineage), 2)
        self.assertEqual(lineage[0], self.command)
        self.assertIsInstance(lineage[1], BasicCommand)
        self.assertEqual(
            subcommand.lineage_names,
            [self.command.name, subcommand.name]
        )

    def test_event_class(self):
        self.command = MockCustomCommand(self.session)
        help_command = self.command.create_help_command()
        self.assertEqual(help_command.event_class, 'mock')
        subcommand = self.command.subcommand_table['basic']
        sub_help_command = subcommand.create_help_command()
        # Note that the name of this Subcommand was never changed even
        # though it was put into the table as ``basic``. If no name
        # is overriden it uses the name ``commandname``.
        self.assertEqual(sub_help_command.event_class, 'mock.commandname')

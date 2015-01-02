import unittest
from unittest import mock
import os

import pathtag


class PathToTagsTest(unittest.TestCase):

    def test_standard_case(self):
        path = 'Beatles/Revolver'
        expected = {'artist': 'Beatles', 'album': 'Revolver'}

        self.assertEqual(pathtag.path_to_tags(path), expected)

    def test_no_album(self):
        path = 'Beatles'
        expected = {'artist': 'Beatles', 'album': 'Unknown'}

        self.assertEqual(pathtag.path_to_tags(path), expected)

    def test_raise_exception_on_empty_path(self):
        with self.assertRaises(pathtag.PathError):
            pathtag.path_to_tags('')

    def test_raise_exception_on_too_nested_path(self):
        with self.assertRaises(pathtag.PathError):
            pathtag.path_to_tags('Beatles/Are/Great')


@mock.patch('pathtag.EasyID3')
class UpdateTagsTest(unittest.TestCase):

    def setUp(self):
        self.filepath = 'MyMusic/Beatles/Revolver/01 - Tax Man.mp3'
        self.new_tags = {'ARTIST': 'Beatles', 'ALBUM': 'Revolver'}

    def test_tagfile_created(self, mock_EasyID3):
        pathtag.update_tags(self.filepath, self.new_tags)

        mock_EasyID3.assert_called_with(self.filepath)

    def test_updating_tags(self, mock_EasyID3):
        tagfile = mock_EasyID3.return_value
        mock_container = {}  # Used for collecting tagfile data
        def setitem(name, val):
            mock_container[name] = val
        tagfile.__setitem__.side_effect = setitem

        pathtag.update_tags('filepath', self.new_tags)

        for key, val in self.new_tags.items():
            self.assertEqual(mock_container[key], [val])

    def test_saving(self, mock_EasyID3):
        tagfile = mock_EasyID3.return_value

        pathtag.update_tags('filepath', self.new_tags)

        tagfile.save.assert_called_with()

    @mock.patch('pathtag.logger')
    def test_log_if_EasyID3_raises(self, mock_logger, mock_EasyID3):
        mock_EasyID3.side_effect = OSError()

        pathtag.update_tags('filepath', self.new_tags)

        mock_logger.info.assert_called_with(
            "mutagen failed to load 'filepath'")


def walk_mock(basedir):
    return [
        ['basedir', ['dir'], []],
        ['basedir/dir', [], ['file.mp3']],
    ]


@mock.patch('pathtag.os')
@mock.patch('pathtag.path_to_tags')
@mock.patch('pathtag.update_tags')
class FixFilesMetadataTest(unittest.TestCase):

    def test_extract_tags(self, mock_update_tags, mock_path_to_tags, mock_os):
        mock_os.walk = walk_mock
        relpath = mock_os.path.relpath.return_value

        pathtag.fix_files_metadata('basedir')

        mock_path_to_tags.assert_called_with(relpath)

    def test_update_file(self, mock_update_tags, mock_path_to_tags, mock_os):
        mock_os.walk = walk_mock
        mock_os.path.join = os.path.join

        pathtag.fix_files_metadata('basedir')

        tags = mock_path_to_tags.return_value
        mock_update_tags.assert_called_with('basedir/dir/file.mp3', tags)

    def test_do_nothing_when_path_is_illegal(self, mock_update_tags,
                                             mock_path_to_tags, mock_os):
        mock_os.walk = walk_mock
        mock_path_to_tags.side_effect = pathtag.PathError()

        pathtag.fix_files_metadata('basedir')

        self.assertFalse(mock_update_tags.called)


if __name__ == '__main__':
    unittest.main()

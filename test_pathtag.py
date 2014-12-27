import unittest
from unittest import mock
import os

import pathtag


class PathToTagsTest(unittest.TestCase):
    
    def test_standard_case(self):
        path = 'Beatles/Revolver'
        expected = {'ARTIST': 'Beatles', 'ALBUM': 'Revolver'}

        self.assertEqual(pathtag.path_to_tags(path), expected)

    def test_no_album(self):
        path = 'Beatles'
        expected = {'ARTIST': 'Beatles', 'ALBUM': 'Unknown'}

        self.assertEqual(pathtag.path_to_tags(path), expected)

    def test_raise_exception_on_empty_path(self):
        with self.assertRaises(pathtag.PathError):
            pathtag.path_to_tags('')

    def test_raise_exception_on_too_nested_path(self):
        with self.assertRaises(pathtag.PathError):
            pathtag.path_to_tags('Beatles/Are/Great')


@mock.patch('pathtag.taglib')
class UpdateTagsTest(unittest.TestCase):

    def setUp(self):
        self.filepath = 'MyMusic/Beatles/Revolver/01 - Tax Man.mp3'
        self.new_tags = {'ARTIST': 'Beatles', 'ALBUM': 'Revolver'}

    def test_tagfile_created(self, mock_taglib):
        pathtag.update_tags(self.filepath, self.new_tags)

        mock_taglib.File.assert_called_with(self.filepath)

    def test_updating_tags(self, mock_taglib):
        tagfile = mock_taglib.File.return_value
        tagfile.tags = {}

        pathtag.update_tags('filepath', self.new_tags)

        self.assertEqual(tagfile.tags, self.new_tags)

    def test_saving(self, mock_taglib):
        tagfile = mock_taglib.File.return_value

        pathtag.update_tags('filepath', self.new_tags)

        tagfile.save.assert_called_with()

    @mock.patch('pathtag.logger')
    def test_log_if_taglib_raises(self, mock_logger, mock_taglib):
        mock_taglib.File.side_effect = OSError()

        pathtag.update_tags('filepath', self.new_tags)

        self.assertTrue(mock_logger.info.called)


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

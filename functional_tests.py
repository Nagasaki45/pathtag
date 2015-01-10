import unittest
import shutil
import os
import tarfile
import subprocess

from mutagen.easyid3 import EasyID3

MATERIALS_DIR = 'test_materials'
BACKUP = 'backup.tar'


class MainTest(unittest.TestCase):

    def setUp(self):
        # Backup MATERIALS_DIR
        with tarfile.TarFile(BACKUP, 'w') as backup:
            backup.add('test_materials')
        # Run pathtag.py on it
        subprocess.check_call(['python', 'pathtag.py', MATERIALS_DIR])

    def tearDown(self):
        # Remove manipulated dir
        shutil.rmtree(MATERIALS_DIR)
        # Restore the backup
        with tarfile.TarFile(BACKUP) as backup:
            backup.extractall()
        # Remove backup
        os.remove(BACKUP)
        
    def load_track(self, *args):
        args = [MATERIALS_DIR] + list(args)
        return EasyID3(os.path.join(*args))

    def test_standard_behavior(self):
        track = self.load_track('artist', 'album', 'track.mp3')
        self.assertEqual(track['artist'], ['artist'])
        self.assertEqual(track['album'], ['album'])

    def test_unknown_album(self):
        track = self.load_track('artist', 'unknown_album_track.mp3')
        self.assertEqual(track['album'], ['Unknown'])

    def test_illegal_path_no_dir(self):
        track = self.load_track('illegal_path_track.mp3')
        self.assertEqual(track['album'], ['asdasd'])  # Original value
        self.assertEqual(track['artist'], ['asdasd'])  # Original value
    
    def test_illegal_path_too_nested(self):
        track = self.load_track(
            'artist', 'album', 'illegal_path_dir', 'illegal_path_track.mp3'
        )
        self.assertEqual(track['album'], ['asdasd'])  # Original value
        self.assertEqual(track['artist'], ['asdasd'])  # Original value


if __name__ == '__main__':
    unittest.main()

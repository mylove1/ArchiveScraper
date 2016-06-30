""" Test DB

"""
import tempfile
import os
import shutil

from nose.tools import assert_equals
from nose.tools import assert_raises

import archiver

# pylint: disable=missing-docstring,no-self-use,attribute-defined-outside-init,too-many-public-methods,protected-access

class TestDB():

    @classmethod
    def setup_class(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.fname = os.path.join(cls.temp_dir, 'test.db')

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.temp_dir)

    def setup(self):
        self.db = archiver.DB(fname = self.fname)

    def teardown(self):
        with self.db.connect() as con:
            self.db.clean(con)

    def test_set_filename(self):
        url = 'wikipedia.org'
        with self.db.connect() as con:
            self.db.set_filename(con, url)
            cur = con.cursor()
            cur.execute('SELECT * FROM file_names')
            assert_equals(cur.fetchone(), (url, 1))

    def test_set_filename_get_row_id(self):
        url = 'wikipedia.org'
        with self.db.connect() as con:
            row_id = self.db.set_filename(con, url)
            assert_equals(row_id, 1)

    def test_set_filename_autoincrement(self):
        with self.db.connect() as con:
            self.db.set_filename(con, 'a')
            self.db.set_filename(con, 'b')
            cur = con.cursor()
            cur.execute('SELECT * FROM file_names')
            result = cur.fetchall()
        assert_equals(result, [('a', 1), ('b', 2)])

    def test_get_filename(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('INSERT INTO file_names (url) VALUES ("wikipedia.org")')
            filename = self.db.get_filename(con, 'wikipedia.org')
            assert_equals(filename, '000001')

    def test_get_filename_raises_KeyError(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('INSERT INTO file_names (url) VALUES ("wikipedia.org")')
            assert_raises(KeyError, self.db.get_filename, con, 'uncyclopedia.org')

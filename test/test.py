from nose.tools import assert_equals, assert_not_equals
from nose.tools import assert_is_instance
from nose.tools import assert_raises, raises
from nose.tools import assert_true, assert_false
import nose

import datetime
import tempfile
import os
import json
import shutil

import archiver

class TestGetArchiveUrls(object):
    @classmethod
    def setup_class(cls):
        cls.data = archiver.get_archive_urls(
            from_date = '2016-04-01',
            url = 'http://politics.people.com.cn/GB/70731/review/{}.html')

    def test_type_urls(self):
        assert_is_instance(self.data, (list,))

    def test_len_urls(self):
        assert_equals(len(self.data), 1517)

    def test_type_url(self):
        assert_is_instance(self.data[0], (str,))

    def test_first_url(self):
        assert_equals(
            self.data[0],
            'http://politics.people.com.cn/GB/70731/review/20160401.html')

    def test_final_url(self):
        assert_equals(
            self.data[-1],
            'http://politics.people.com.cn/GB/70731/review/20120206.html')

    def test_from_date_not_string(self):
        assert_raises(TypeError, archiver.get_archive_urls, 20160401)

    def test_from_date_string_wrong_format(self):
        assert_raises(ValueError, archiver.get_archive_urls, '2016-4-1')

class TestGetDateStringeGenerator(object):
    def setup(self):
        self.dates = archiver.get_date_string_generator(
            from_date = '2015-04-01',
            earliest_date='2015-01-01',
            date_formatter=archiver.get_date_as_string_YYYYmmdd)

    def test_first_date(self):
        for generator_item, number in zip(self.dates, ['20150401']):
            assert_equals(generator_item, number)

    def test_len(self):
        assert_equals(len(list(self.dates)), 91)

    def test_first_date_YYYY_mm_dd(self):
        dates = archiver.get_date_string_generator(
            from_date = '2015-04-01',
            earliest_date='2015-01-01',
            date_formatter=archiver.get_date_as_string_YYYY_mm_dd)
        for generator_item, number in zip(dates, ['2015-04-01']):
            assert_equals(generator_item, number)

class TestGetDateAsString(object):
    def test_input_not_date_time(self):
        assert_raises(
            TypeError,
            archiver.get_date_as_string_YYYY_mm_dd,
            '2015-09-01')

    def test_input_date_time(self):
        date_string = '2015-09-01'
        assert_equals(
            archiver.get_date_as_string_YYYY_mm_dd(
                datetime.datetime.strptime(date_string, '%Y-%m-%d')),
            date_string)

    def test_input_not_date_time(self):
        assert_raises(
            TypeError,
            archiver.get_date_as_string_YYYYmmdd,
            '2015-09-01')

    def test_input_date_time(self):
        date_string = '20150901'
        assert_equals(
            archiver.get_date_as_string_YYYYmmdd(
                datetime.datetime.strptime(date_string, '%Y%m%d')),
            date_string)

class TestGetDate(object):
    def test_date(self):
        assert_equals(
            archiver.get_date('2016-06-06'),
            datetime.datetime.strptime('20160606', '%Y%m%d'))

    def test_not_string(self):
        assert_raises(TypeError, archiver.get_date, 20160606)

    def test_wrong_format(self):
        assert_raises(ValueError, archiver.get_date, '06=06-2016')

class TestDearchiver(object):
    @classmethod
    def setup_class(cls):
        cls.temp_dir = tempfile.mkdtemp()
        os.mkdir(cls.temp_dir + '/archive')
        cls.archive = archiver.get_archive_urls(
            from_date = '2016-04-01',
            earliest_date='2012-02-06',
            url = 'http://politics.people.com.cn/GB/70731/review/{}.html'
        )

    @classmethod
    def teardown_class(cls):
        #cls.dearch._.close()
        shutil.rmtree(cls.temp_dir)

    def setup(self):
        self.dearch = archiver.Dearchiver(
            directory = self.temp_dir, silent = True)

    def teardown(self):
        self.dearch.clean(silent = True)

    def test_init_dir_not_string(self):
        assert_raises(
            TypeError, archiver.Dearchiver,
            directory = 1, silent = True)

    def test_init_dir_not_path(self):
        assert_raises(
            ValueError, archiver.Dearchiver,
            directory = '', silent = True)

    def test_isdir_temp(self):
        assert_true(os.path.isdir(self.temp_dir))

    def test_isfile_archive_json_file(self):
        assert_true(os.path.isfile(self.dearch.archive_json_file))

    def test_isfile_scanned_json_file(self):
        assert_true(os.path.isfile(self.dearch.scanned_json_file))

    def test_isfile_article_json_file(self):
        assert_true(os.path.isfile(self.dearch.article_json_file))

    def test_len_of_archive(self):
        assert_equals(len(self.archive), 1517)

    def test_clean(self):
        self.dearch.clean(silent = True)
        assert_false(os.path.isfile(self.dearch.archive_json_file))
        assert_false(os.path.isfile(self.dearch.scanned_json_file))
        assert_false(os.path.isfile(self.dearch.article_json_file))

    def test__load_archive_json_creation(self):
        self.dearch._load_archive_json()
        assert_is_instance(self.dearch.archive_meta, dict)
        assert_equals(self.dearch.archive_meta, {})

    def test__load_archive_json_contents(self):
        # Manually construct and save the file:
        json.dump(
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}},
            open(self.dearch.archive_json_file, 'w'))

        # Load file:
        self.dearch._load_archive_json()
        assert_equals(
            self.dearch.archive_meta,
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

    def test__save_archive_url(self):
        # Init file:
        self.dearch._save_archive_url('www.example.com', '000001')

        # Manually load the dict from file and compare:
        assert_equals(
            json.load(open(self.dearch.archive_json_file)),
            {'www.example.com': {'f': '000001'}})

    def test__save_archive_links(self):
        # Init file:
        self.dearch._save_archive_links('www.example.com', ['www.link.com'])

        # Manually load the dict from file and compare:
        assert_equals(
            json.load(open(self.dearch.archive_json_file)),
            {'www.example.com': {'l': ['www.link.com']}})

    def test__save_archive_url_and_links(self):
        # Init file:
        self.dearch._save_archive_url('www.example.com', '000001')
        self.dearch._save_archive_links('www.example.com', ['www.link.com'])

        # Manually load the dict from file and compare:
        assert_equals(
            json.load(open(self.dearch.archive_json_file)),
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

    def test__get_filename_wrong_type(self):
        assert_raises(TypeError, self.dearch._get_filename, ['not a string'])

    def test__get_filename_key_not_registered(self):
        self.dearch._load_archive_json()
        assert_raises(KeyError, self.dearch._get_filename, 'www.example.com')

    def test__get_filename(self):
        self.dearch._load_archive_json()
        fname = '000001'
        fpath = self.dearch.directory + '/archive/' + fname
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        self.dearch._save_archive_url('www.example.com', fname)
        assert_equals(self.dearch._get_filename('www.example.com'), fname)

    def test__get_filepath_wrong_type(self):
        assert_raises(TypeError, self.dearch._get_filepath, ['not a string'])

    def test__get_filepath_key_not_registered(self):
        self.dearch._load_archive_json()
        assert_raises(KeyError, self.dearch._get_filepath, 'www.example.com')

    def test__get_filepath_file_does_not_exist(self):
        self.dearch._load_archive_json()
        self.dearch._save_archive_url('www.example.com', '000001')
        assert_raises(IOError, self.dearch._get_filepath, 'www.example.com')

    def test__get_filepath(self):
        self.dearch._load_archive_json()
        fname = '000001'
        fpath = self.dearch.directory + '/archive/' + fname
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        self.dearch._save_archive_url('www.example.com', fname)
        assert_equals(self.dearch._get_filepath('www.example.com'), fname)

    def test__load_archive_pages(self):
        self.dearch._load_archive_json()
        self.dearch._save_archive_url('www.example.com', '000001')
        fname = '000001'
        fpath = self.dearch.directory + '/archive/' + fname
        with open(fpath, 'wb') as f: f.write(b'Some contents')

        self.dearch.load_archive_pages('www.example.com')
        #assert_equal


    def test__get_filepath(self):
        pass

    def test_get_soup_file_not_exists(self):
        assert_raises(IOError, self.dearch.get_soup, '000001')

    def test_get_soup(self):
        self.dearch._load_archive_json()
        fname = '000001'
        fpath = self.dearch.directory + '/archive/' + fname
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        self.dearch._save_archive_url('www.example.com', fname)
        soup = self.dearch.get_soup(fpath)
        assert_equals(soup.text, 'Some contents')

    def test_get_soup_filename_not_a_string(self):
        not_a_string = 1
        assert_raises(TypeError, self.dearch.get_soup, not_a_string)

    def test_get_soup_url_not_a_string(self):
        string = '000001'
        not_a_string = 1
        assert_raises(TypeError, self.dearch.get_soup, string, not_a_string)

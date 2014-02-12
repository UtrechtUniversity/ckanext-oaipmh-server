# coding: utf-8
#
# pylint: disable=no-self-use, missing-docstring, too-many-public-methods, invalid-name

"""
Unit tests for OAI-PMH harvester.
"""
import bs4
from lxml import etree

from unittest import TestCase
import lxml

import ckan
from ckanext.oaipmh.harvester import OAIPMHHarvester
import ckanext.harvest.model as harvest_model
import ckanext.kata.model as kata_model
from ckanext.oaipmh.oai_dc_reader import dc_metadata_reader, _filter_tag_name_namespace, NS, _get_data_pids, _get_download, _get_version_pid, _get_checksum, _get_org_auth

FIXTURE_HELDA = "ckanext-oaipmh/ckanext/oaipmh/test_fixtures/helda_oai_dc.xml"
FIXTURE_IDA = "ckanext-oaipmh/ckanext/oaipmh/test_fixtures/oai-pmh.xml"

class TestOAIPMHHarvester(TestCase):

    @classmethod
    def setup_class(cls):
        '''
        Setup database and variables
        '''
        harvest_model.setup()
        kata_model.setup()
        cls.harvester = OAIPMHHarvester()

    @classmethod
    def teardown_class(cls):
        ckan.model.repo.rebuild_db()

    def test_harvester_info(self):
        info = self.harvester.info()
        assert isinstance(info, dict)

    def test_gather_stage(self):
        # gather_stage should throw some exception with parameter None
        self.assertRaises(Exception, self.harvester.gather_stage, (None))

    def test_fetch_stage(self):
        # should throw some exception with parameter None
        self.assertRaises(Exception, self.harvester.fetch_stage, (None))

    def test_import_stage(self):
        # should return false
        assert not self.harvester.import_stage(None)


# class TestImportCore(TestCase):
#
#     def test_harvester_info(self):
#         parse_xml = generic_xml_metadata_reader
#         assert isinstance(info, dict)

class TestOAIDCReaderHelda(TestCase):
    '''
    Tests for reading OAI_DC metadata generated from Helda
    '''

    @classmethod
    def setup_class(cls):
        '''
        Setup variables
        '''
        cls.xml_file = open(FIXTURE_HELDA, 'r')
        cls.xml = cls.xml_file.read()

        cls.bs = bs4.BeautifulSoup(cls.xml, 'xml')
        cls.dc = cls.bs.metadata.dc

    @classmethod
    def teardown_class(cls):
        pass

    def test_dc_metadata_reader(self):
        '''
        Test reading a whole file
        '''

        metadata = dc_metadata_reader(etree.fromstring(self.xml))

        assert metadata

        assert 'unified' in metadata.getMap()
        assert 'availability' in metadata.getMap()['unified']

    def test_filter_tag_name_namespace(self):

        output = _filter_tag_name_namespace('creator', NS['dc'])
        creators = [creator for creator in self.dc(output, recursive=False)]

        assert len(creators) == 3

    def test_get_data_pids(self):

        expected_pids = set([u'http://link.aip.org/link/?jcp/123/064507', u'http://hdl.handle.net/10138/1074'])
        output = _get_data_pids(self.dc)

        assert set(output) == expected_pids

    def test_get_download(self):
        output = _get_download(self.dc)

        # We should get atleast some download link from the pids:
        assert len(list(output)) > 0

    def test_get_org_auth(self):
        output = _get_org_auth(self.dc)

        assert output

class TestOAIDCReaderIda(TestCase):

    @classmethod
    def setup_class(cls):
        '''
        Setup variables
        '''
        cls.xml_file = open(FIXTURE_IDA, 'r')
        cls.xml = cls.xml_file.read()

        cls.bs = bs4.BeautifulSoup(cls.xml, 'xml')
        cls.dc = cls.bs.metadata.dc

    @classmethod
    def teardown_class(cls):
        pass

    def test_dc_metadata_reader(self):
        '''
        Test reading a whole file
        '''

        metadata = dc_metadata_reader(etree.fromstring(self.xml))

        assert metadata

        assert 'unified' in metadata.getMap()
        assert 'availability' in metadata.getMap()['unified']

    def test_get_version_pid(self):

        pid = _get_version_pid(self.dc)

        assert pid
        assert 'ida' in next(pid)

    def test_get_checksum(self):

        hash = _get_checksum(self.dc)

        assert hash == u'7932df5999a30bb70871359f700dbe23'

    def test_get_download(self):
        output = _get_download(self.dc)

        # We should get atleast some download link:
        assert len(list(output)) > 0

from iso639 import languages
from lxml.etree import SubElement
from lxml.etree import Element
from oaipmh.server import NS_XSI
import re

NS_OAIDATACITE = 'http://schema.datacite.org/oai/oai-1.0/'
NS_DATACITE = 'http://datacite.org/schema/kernel-4'
event_to_dt = {'collection': 'Collected',
               'creation': 'Created',
               'extended': 'Updated',
               'changed': 'Updated',
               'published': 'Issued',
               'sent': 'Submitted',
               'received': 'Accepted',
               'modified': 'Updated'}


def _parse_orcid(creator):
    orcids = re.findall(r"\(ORCID: ([\d-]+)\)", creator)
    if orcids:
        name = creator.split(' (')[0]
        orcid = orcids[0]
    else:
        name = creator
        orcid = None
    return name, orcid

def _map_resource_type(resource_type):
    val = resource_type.lower()
    if re.search(r'.*photo|image.*', val):
        rtg = 'Image'
    elif re.search(r'.*data|questionnaire.*', val):
        rtg = 'Dataset'
    elif re.search(r'.*computer program|jupyter|software|source code.*', val):
        rtg = 'Software'
    elif re.search(r'journal article', val):
        rtg = 'Article'
    elif re.search(r'.*audio.*', val):
        rtg = 'Audiovisual'
    elif re.search(r'conference paper', val):
        rtg = 'Conference object'
    else:
        rtg = 'Other'
    return rtg

def _convert_language(lang):
    '''
    Convert alpha2 language (eg. 'en') to terminology language (eg. 'eng')
    '''
    try:
        lang_object = languages.get(part2t=lang)
        return lang_object.part1
    except KeyError as ke:
        # TODO: Parse ISO 639-2 B/T ?
        # log.debug('Invalid language: {ke}'.format(ke=ke))
        return ''


def _append_agent(e_agent_parent, role, key, value, roletype=None):
    for agent in value:
        e_agent = SubElement(e_agent_parent, nsdatacite(role))
        if roletype:
            e_agent.set(role + 'Type', roletype)
        agentname = role + 'Name'
        e_agent_name = SubElement(e_agent, nsdatacite(agentname))
        e_agent_name.text = agent['name']
        org = agent.get('organisation')
        if org:
            e_affiliation = SubElement(e_agent, nsdatacite('affiliation'))
            e_affiliation.text = org


def datacite_writer(element, metadata):
    '''Transform oaipmh.common.Metadata metadata dictionaries to lxml.etree.Element XML documents.
    '''
    e_r = SubElement(element, nsdatacite('resource'), nsmap={None: NS_DATACITE, 'xsi': NS_XSI})
    e_r.set('{%s}schemaLocation' % NS_XSI, '%s http://schema.datacite.org/meta/kernel-4.3/metadata.xsd' % NS_DATACITE)

    alt_id_exists = False

    map = metadata.getMap()
    for k, v in map.items():
        if v:
            print(k)
            print(v)
            if k == 'version':
                if v:
                    e_version = SubElement(e_r, nsdatacite('version'))
                    e_version.text = str(v[0])
                continue
            if k == 'titles':
                e_titles = SubElement(e_r, nsdatacite(k))
                e_title_primary = SubElement(e_titles, nsdatacite('title'), language=v[0]['lang'])
                e_title_primary.text = v[0]['title']
                continue
            if k == 'descriptions':
                e_descs = SubElement(e_r, nsdatacite(k))
                e_desc = SubElement(e_descs, nsdatacite('description'), descriptionType="Abstract")
                e_desc.text = v[0]
                continue
            if k == 'resourceType':
                # rtg = _map_resource_type(v[0])
                e_resourceType = SubElement(e_r, nsdatacite(k), resourceTypeGeneral=v['resourceTypeGeneral'])
                e_resourceType.text = v['resourceType']
                continue
            if k == 'subjects':
                e_subjects = SubElement(e_r, nsdatacite(k))
                for subject in v:
                    # 'subject': moc['dc_mode_of_collection'], 'subjectScheme':
                    e_subject = SubElement(e_subjects, nsdatacite('subject'), subjectScheme=subject['subjectScheme'])
                    e_subject.text = subject['subject']
                continue
            if k == 'creator':
                e_creators = SubElement(e_r, nsdatacite('creators'))
                for creator in v:
                    # v['name'], v['nameType']
                    e_creator = SubElement(e_creators, nsdatacite(k))
                    e_creatorName = SubElement(e_creator, nsdatacite('creatorName'), nameType=creator['nameType'])
                    e_creatorName.text = creator['name']
                    
                continue
                # for creatorName in v:
                #    name,orcid = _parse_orcid(creatorName)
                #    e_creator = SubElement(e_creators, nsdatacite(k))
                #    e_creatorName = SubElement(e_creator, nsdatacite('creatorName'))
                #    e_creatorName.text = name
                #    if orcid:
                #        e_nameIdentifier = SubElement(e_creator, nsdatacite('nameIdentifier'), nameIdentifierScheme='ORCID')
                #        e_nameIdentifier.text = orcid
                continue
            if k == 'contributor':
                # No contributors at this time
                e_contributors = SubElement(e_r, nsdatacite('contributors'))
                for contributorName in v:
                    e_contributor = SubElement(e_contributors, nsdatacite(k), contributorType="Other")
                    e_contributorName = SubElement(e_contributor, nsdatacite('contributorName'))
                    e_contributorName.text = contributorName
                continue
            if k == 'publisher':
                # 'Name': study_publisher['study_publisher_name'],
                #                       'Identifier': study_publisher['study_publisher_identifier'],
                #                       'IdentifierType': study_publisher['study_publisher_identifier_type']
                # Only take the first
                e_publisher = SubElement(e_r, nsdatacite('publisher'), Identifier=v[0]['Identifier'], IdentifierType=v[0]['IdentifierType'])
                e_publisher.text = v[0]['Name']
                continue
            if k == 'language':
                e_language = SubElement(e_r, nsdatacite('language'))
                e_language.text = v[0]
                continue
            if k == 'format':
                e_formats = SubElement(e_r, nsdatacite('formats'))
                for format in v:
                    e_format = SubElement(e_formats, nsdatacite(k))
                    e_format.text = format
                continue
            if k == 'size':
                e_sizes = SubElement(e_r, nsdatacite('sizes'))
                for size in v:
                    e_size = SubElement(e_sizes, nsdatacite(k))
                    e_size.text = size
                continue
            if k == 'publicationYear':
                e_publicationYear = SubElement(e_r, nsdatacite('publicationYear'))
                e_publicationYear.text = str(v[0])
                continue
            if k == 'spatialCoverage':
                if v:
                    e_spatial_coverages = SubElement(e_r, nsdatacite('geoLocations'))
                    e_spatial_coverage = SubElement(e_spatial_coverages, nsdatacite('geoLocation'))
                    # Only take first one into account
                    if v[0]:
                        # [{'geoLocationPlace': 'NL'}]
                        e_spatial_places = SubElement(e_spatial_coverage, nsdatacite('geoLocationPlace'))
                        e_spatial_places.text = v[0]['geoLocationPlace']
                    '''
                    if v[1]:
                        values = v[1].split(',')
                        e_point = SubElement(e_spatial_coverage, nsdatacite('geoLocationPoint'))
                        e_point_long = SubElement(e_point, nsdatacite('pointLongitude'))
                        e_point_long.text = values[0]
                        e_point_lat = SubElement(e_point, nsdatacite('pointLatitude'))
                        e_point_lat.text = values[1]
                    elif v[2]:
                        values = v[2].split(',')
                        e_bbox = SubElement(e_spatial_coverage, nsdatacite('geoLocationBox'))
                        e_bbox_west = SubElement(e_bbox, nsdatacite('westBoundLongitude'))
                        e_bbox_west.text = values[0]
                        e_bbox_east = SubElement(e_bbox, nsdatacite('eastBoundLongitude'))
                        e_bbox_east.text = values[1]
                        e_bbox_south = SubElement(e_bbox, nsdatacite('southBoundLatitude'))
                        e_bbox_south.text = values[2]
                        e_bbox_north = SubElement(e_bbox, nsdatacite('northBoundLatitude'))
                        e_bbox_north.text = values[3]
                    '''
                continue
            if k == 'rights':
                e_rightslist = SubElement(e_r, nsdatacite('rightsList'))
                for rights in v:
                    # {'rights': access['study_data_access_description'],
                    #                    'rightsUri': access['study_data_access_URL']}
                    e_rights = SubElement(e_rightslist, nsdatacite(k), rightsURI=rights['rightsUri'])
                    e_rights.text = rights['rights']
                continue
            if k == 'fundingReference':
                e_funds = SubElement(e_r, nsdatacite('fundingReferences'))
                for fund in v:
                    fund_parts = [''] * 6
                    count = 0
                    values = fund.split('|')[:6]
                    for value in values:
                        fund_parts[count] = value
                        count += 1
                    e_fund = SubElement(e_funds, nsdatacite('fundingReference'))
                    e_fund_name = SubElement(e_fund, nsdatacite('funderName'))
                    e_fund_name.text = fund_parts[0]
                    e_fund_identifier = SubElement(e_fund, nsdatacite('funderIdentifier'), funderIdentifierType=fund_parts[2])
                    e_fund_identifier.text = fund_parts[1]
                    e_fund_award_number = SubElement(e_fund, nsdatacite('awardNumber'), awardURI=fund_parts[4])
                    e_fund_award_number.text = fund_parts[3]
                    e_fund_award_title = SubElement(e_fund, nsdatacite('awardTitle'))
                    e_fund_award_title.text = fund_parts[5]
                continue
            if k == 'dates':
                e_dates = SubElement(e_r, nsdatacite(k))
                for event in v:
                    # {'date': '{}/{}'.format(start, end),
                    #              'dateType': 'Collected',
                    #              'dateInformation': wave['wave_description']}
                    e_date = SubElement(e_dates, nsdatacite('date'), dateType=event['dateType'], dateInformation=event['dateInformation'])
                    e_date.text = event['date']
                    # e_date.set('dateType', 'Collected')
                    # e_date.set('dateType', event_to_dt[event['type']])
                continue
            if k == 'DOI':
                e_id = SubElement(e_r, nsdatacite('identifier'), identifierType='DOI')
                e_id.text = v[0]
                continue
            if k == 'PID':
                if map['DOI']:
                    continue
                e_id = SubElement(e_r, nsdatacite('identifier'), identifierType='Handle')
                e_id.text = v[0]
                continue
            if k == 'source':
                if map['DOI']:
                    continue
                if map['PID']:
                    continue
                e_id = SubElement(e_r, nsdatacite('identifier'), identifierType='URL')
                e_id.text = v[0]
                continue
            if k == 'relatedIdentifier':
                e_rel_ids = SubElement(e_r, nsdatacite('relatedIdentifiers'))
                for relid in v:
                    relid_parts = [""] * 3
                    # count = 0
                    # values = relid.split("|")[:3]
                    # for value in values:
                    #    relid_parts[count] = value
                    #    count += 1
                    # url = relid_parts[0]
                    # id_type = relid_parts[1]
                    # rel_type = relid_parts[2]
                    # e_rel_id = SubElement(e_rel_ids, nsdatacite('relatedIdentifier'), relatedIdentifierType=id_type, relationType=rel_type)
                    # e_rel_id.text = url
                    e_rel_id = SubElement(e_rel_ids, nsdatacite('relatedIdentifier'), relatedIdentifierType=relid['relatedIdentifierType'], relationType=relid['relationType'])
                    e_rel_id.text = relid['relatedIdentifier']
                continue


def nsdatacite(name):
    return '{%s}%s' % (NS_DATACITE, name)


def nsoaidatacite(name):
    return '{%s}%s' % (NS_OAIDATACITE, name)

from __future__ import print_function

import json
import os
import logging
import xml.parsers.expat


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

try:
    import lxml
    from lxml import etree
except ImportError:
    logger.error("Module lxml import error")

import requests





def validate(fname, schema_name):

    is_valid = None
    reason = 'Unknwon'
    xmlschema = None


    #with open(schema) as f:
    #    doc = etree.parse(schema)
    with open(schema_name) as f:
        try:
            doc = etree.parse(f)
            logger.debug(f.read())
        except:
            return(is_valid, 'Cannot parse schame')

    #print "Validating schema ... "
    try:
        xmlschema = etree.XMLSchema(doc)
        logger.debug('schema')
        logger.debug(xmlschema)
    except lxml.etree.XMLSchemaParseError as e:
        reason = e
        logger.debug(e)
        return (is_valid, e)


    #print "Schema OK"
    if xmlschema is None:
        logger.debug('schema is None')
        return (None, 'No schema')

    with open(fname) as f:
        try:
            doc = etree.parse(f)
            logger.debug(fname)
            logger.debug(doc)
        except lxml.etree.XMLSyntaxError as e:
            is_valid = False
            reason = e
            logger.debug(e)
            return (None, e)

    #print "Validating document ..."
    try:
        xmlschema.assertValid(doc)
        
        logger.debug('assertValid')
    except lxml.etree.DocumentInvalid as e:
        #print e
        is_valid = False
        logger.debug(e)
        return (is_valid, str(e))
    except lxml.etree.XMLSyntaxError as e:
        #print e
        is_valid =  False
        logger.debug(e)
        return (is_valid, str(e))
    except:
        return(False, 'Validation failed for an unknown reason')

    #print "Document OK"
    if xmlschema is not None:
      log = xmlschema.error_log
      error = log.last_error
      logger.debug(error)

    return (is_valid, reason)


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    if not 'url' in event:
        return {'status': 'error', 'message': 'No KML url given'}

    kml_url = event['url']

    content = None
    is_valid = False
    xml = None
    r = requests.get(kml_url, stream=True)

    if r.status_code == 200:
        kml_string = requests.get(kml_url).content
        tmp_kml = os.path.join('/tmp', os.path.basename(kml_url))
        with open(tmp_kml, 'w') as f:
            f.write(kml_string)

        ''' r.raw.decode_content = True
        content = r.raw
        tmp_kml = os.path.join('/tmp', os.path.basename(kml_url))
        with open(tmp_kml, 'w') as f:
            f.write(content)
        '''
        schema = 'schemas/ogckml22.xsd'    

        (is_valid, reason) = validate(tmp_kml, schema)

        return {'status': 'done', 'url': kml_url, 'schema': os.path.basename(schema), 'valid': is_valid, 'reason': reason }
    else:
      return {'status': 'error', 'message': 'Cannot download KML {}'.format(kml_url)}




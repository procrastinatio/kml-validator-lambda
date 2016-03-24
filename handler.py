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





def validate(file_fullpath, schema_name):

    xmlschema = None
    status ='unknwon'
    fname = os.path.basename(file_fullpath)
    


    with open(schema_name) as f:
        try:
            doc = etree.parse(f)
            logger.debug(f.read())
        except:
             msg = "Cannot read schema '{}'".format(schema_name)
             logger.error(msg)

             return('error', msg)

    #print "Validating schema ... "
    try:
        xmlschema = etree.XMLSchema(doc)
        logger.debug('schema')
        logger.debug(xmlschema)
    except lxml.etree.XMLSchemaParseError as e:
        msg = "Cannot parse schema '{}'".format(schema_name)
        logger.debug(e)
        return ('error', msg)


    #print "Schema OK"
    if xmlschema is None:
        logger.debug('schema is None')
        return ('error', 'No schema')

    with open(file_fullpath) as f:
        try:
            doc = etree.parse(f)
            logger.debug(file_fullpath)
            logger.debug(doc)
        except lxml.etree.XMLSyntaxError as e:
            msg = "XML syntax error in kml '{}'".format(fname)
            logger.debug(e)
            return ('error', msg)

    #print "Validating document ..."
    try:
        xmlschema.assertValid(doc)
        
        logger.debug('assertValid')
    except lxml.etree.DocumentInvalid as e:
        logger.debug(e)
        msg = "KML document '{}' is invalid\n\n{}".format(fname, repr(e))
        return ('invalid', msg)
    except lxml.etree.XMLSyntaxError as e:
        #print e
        msg = "KML document '{}' has syntax error(s)\n\n{}".format(fname, repr(e))
        logger.debug(e)
        return ('invalid', msg)
    except:
        return('invalid', 'Validation failed for an unknown reason')

    #print "Document OK"
    if xmlschema is not None:
      log = xmlschema.error_log
      error = log.last_error
      logger.debug(error)

    return ('valid', 'KML is valid')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    
    schema = 'schemas/ogckml22.xsd'    

    warnings = []
    errors = []

    if not 'url' in event:
        return {'status': 'error', 'message': 'No KML url given'}

    kml_url = event['url']

    content = None
    r = requests.get(kml_url, stream=True)

    if r.status_code == 200:
        content_type = r.headers.get('content-type')
        if content_type =='application/vnd.google-earth.kmz':
             return {'status': 'error', 'url': kml_url, 'schema': os.path.basename(schema),  'message': 'KMZ are not supported now' }

        if content_type != 'application/vnd.google-earth.kml+xml':
             warnings.append('Set the "Content-Type" to "application/vnd.google-earth.kml+xml" please')

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

        (status, msg) = validate(tmp_kml, schema)

        return {'status': status, 'url': kml_url, 'schema': os.path.basename(schema),  'message': msg , 'warnings': warnings}
    else:
        return {'status': 'error', 'url': kml_url, 'schema': os.path.basename(schema), 'message': 'Cannot download KML {}'.format(kml_url), 'warnings': warnings}




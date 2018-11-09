#!/usr/bin/env python

"""
This tool used for copy elasticsearch templates from input to output.

Author: cool_breeze@163.com
Date: 2018/11/01
"""
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import json
import traceback
import httplib
import urllib
import urllib2
import time
import os
import sys, getopt

httplib._MAXHEADERS = 1000
logger = ''

def init_logger(log_file):
    """
    init log
    """
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 60, backupCount=2)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def http_get(url, data=None):
    """
    http get request
    """
    global logger
    logger.info("GET " + url)
    try:
        if data is not None:
            data = urllib.urlencode(data)
            req = urllib2.Request(url, data)
        else:
            req = urllib2.Request(url)
        # response = urllib2.urlopen(req, timeout=10)
        response = urllib2.urlopen(req)
        logger.info("GET {}, Response Code: {}".format(url, str(response.getcode())))
        if response.getcode() == 200:
            return response.read().decode('utf-8')
        else:
            logger.error("curl " + url + " failed with http code " + str(response.getcode()))
            return 'err'
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        return 'err'

def http_post(url, data=None):
    """
    http post request
    """
    global logger
    logger.info("POST " + url)
    try:
        if data is not None:
            req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        else:
            req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        logger.info("POST " + url + ", Response Code: " + str(response.getcode()))
        if response.getcode() == 200:
            return response.read().decode('utf-8')
        else:
            logger.error("curl " + url + " failed with http code " + str(response.getcode()))
            logger.error(response)
            return 'err'
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        return 'err'

def http_delete(url, data=None):
    """
    http delete request
    """
    global logger
    logger.info("DELETE " + url)
    try:
        if data is not None:
            data = urllib.urlencode(data)
            req = urllib2.Request(url, data)
        else:
            req = urllib2.Request(url)
        req.get_method = lambda:'DELETE'
        response = urllib2.urlopen(req)
        logger.info("DELETE " + url + ", Response Code: " + str(response.getcode()))
        if response.getcode() == 200:
            return response.read().decode('utf-8')
        else:
            logger.error("curl " + url + " failed with http code " + str(response.getcode()))
            return 'err'
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        return 'err'

def json_decode(json_str):
    """
    parse str to json
    """
    global logger
    try:
        json_data = json.loads(json_str)
        return json_data
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        return 'err'

def json_encode(json_data):
    """
    make json to str
    """
    global logger
    try:
        json_str = json.dumps(json_data)
        return json_str
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        return 'err'

def main(argv):
    input = ''
    output = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input=", "output="])
    except getopt.GetoptError:
        print 'templatedump.py -i <input_url> -o <output_url>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'templatedump.py -i <input_url> -o <output_url>'
        elif opt in ("-i", "--input"):
            input = arg
        elif opt in ("-o", "--output"):
            output = arg
    if input != '' and output != '':
        print 'Input url: ', input
        print 'Output url: ', output
        """
        request input url for templates
        """
        response = http_get(input)
        if response != None and response != '' and response != "err":
            response = json_decode(response)
            # print "Tempalte Size: %d" % len(response)
            logger.info("Tempalte Size: " + str(len(response)))
            for key, value in response.iteritems():
                # print "response[%s]=" % key, len(value)
                logger.info("response[{}]={}".format(key, len(value)))
                if key != "":
                    templateJson = json_encode(value)
                    # logger.info(templateJson)
                    res = json_decode(http_post(output + "/" + key, templateJson))
                    if res != None and res != '' and res != "err":
                        if res["acknowledged"] == 'true':
                            # print "Create  template %s" % key, "Successfully!"
                            logger.info("Create  template {} Successfully!".format(key))
                        else:
                            # print "Create  template %s" % key, "Fail!"
                            logger.info("Create  template {} Fail!".format(key))

if __name__ == '__main__':
    init_logger("./main.log")
    main(sys.argv[1:])

#!/usr/bin/python

import csv
import json
import random
import re
import sys
import urllib2
import time
import traceback

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i6sf  sf sjf dskfj jlkj sf86) Gecko/20071127 Firefox/2.0.0.11'),
                     ("Accept", "only the best"),
                     ("Accept encoding", "text") ]
print opener.__dict__

MINUTES_RE = re.compile("(\d+) mins")

def ParseTime(s):
    m = MINUTES_RE.match(s)
    assert m, "Could not handle time: '%s'" % s

    return int(m.group(1))

def HandleRoute(start_lat, start_lng,
                end_lat, end_lng,
                addresses={}):

    request = ("http://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&sensor=false&departure_time=1350320798&mode=transit"
               % ("%s,%s" % (start_lat, start_lng),
                  "%s,%s" % (end_lat, end_lng)))

    #request = "http://www.myhttp.info"
    f = opener.open(request).read()
    #print f
    #sys.exit(1)
    #f = urllib2.urlopen(request).read()
    result = json.loads(f)
    routes = result["routes"]

    intersections = {}
    best_duration = 100000

    # First, find the best route.
    for route in routes:
        route_duration = 0
        legs = route["legs"]
        for leg in legs:
            duration_seconds = leg["duration"][u"value"]
            route_duration += duration_seconds

        if route_duration < best_duration:
            best_duration = route_duration

    # Find intersections by lat / long.
    for route in routes:
        rout_duration = 0
        legs = route["legs"]
        last_road = None
        last_lat = None
        last_lng = None
        for i, leg in enumerate(legs):
            addresses[leg["start_address"]] = (leg["start_location"]["lat"],
                                               leg["start_location"]["lng"])
                               
            addresses[leg["end_address"]] = (leg["end_location"]["lat"],
                                             leg["end_location"]["lng"])
                               
    if best_duration > 40000:
        print f
    return best_duration

def SaveAddresses(addresses):
    out_file = open("addresses.csv", "wa")
    writer = csv.writer(out_file)
    writer.writerow([ "lat", "lng", "address" ])
    for address, (lat, lng) in addresses.items():
        writer.writerow([lat, lng, address])

    out_file.close()


def SaveDurations(durations):
    out_file = open("durations.csv", "wa")
    writer = csv.writer(out_file)
    writer.writerow([ "lat", "lng", "duration" ])
    for (slat, slng, elat, elng), duration in durations.items():
        writer.writerow([slat, slng, elat, elng, duration])

    out_file.close()


if __name__ == '__main__':
    pos_list = "37.7,-122.55|"
    pos_list = "37.7,-122.53|37.81,-122.38"
    start = "37.75,-122.4"
    end = "37.78,-122.42"

    addresses = {}
    durations = {}
    print "handle route."
    start_lat = 37.7
    while start_lat <= 37.81:
        start_lat += 0.002

        start_lng = -122.53
        while start_lng <= -122.38:
            start_lng += 0.002

            end_lat = 37.7
            while end_lat <= 37.81:
                end_lat += 0.002

                end_lng = -122.53
                while end_lng <= -122.38:
                    end_lng += 0.002

                    key = (start_lat, start_lng, end_lat, end_lng)
                    if random.random() > 0.00003:
                        continue

                    print "Fetching, ", start_lat, start_lng, "->", end_lat, end_lng
                    try:
                        duration = HandleRoute(start_lat, end_lng,
                                               end_lat, start_lng,
                                               addresses)
                        time.sleep(2)
                        
                    except:
                        duration = 100000
                        print "Failed to process route."
                        traceback.print_exc()
                    if duration < 100000:
                        durations[key] = duration
                        print "  --> ", durations[key]

    SaveDurations(durations)
    SaveAddresses(addresses)

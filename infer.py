#!/usr/bin/python

import numpy as np
import csv
import random
from scipy import optimize

class NP:
    def array(self, x):
        return x

    def dot(self, x, y):
        return x[0] * y[0] + x[1] * y[1]

    def zeros_like(self, x):
        return x

class Point:
    def __init__(self, lat, lng):
        self.cartesian_x = np.array([lat, lng])
        self.metric_x = np.array([lat, lng])
        self.lat = lat
        self.lng = lng
        self.neighbors = {}
        self.address = ""

    def __str__(self):
        return "lat: %.4f, lng: %.4f, cartesian: %s, metric: %s" % (
            self.lat, self.lng, self.cartesian_x, self.metric_x)

    def AddNeighbor(self, other, duration):
        # Ensure that all durations are at least a minute.
        if duration < 60:
            print >>sys.stderr, "Warning.  Low duration."
            duration = 60

        if other not in self.neighbors:
            self.neighbors[other] = duration

    def Gradient(self, this_x, neighbors):
        coeffs = 0.
        gradient = 0.
        for neighbor, distance in neighbors.items():
            coeff = 2 * (np.dot(x - y, x - y) - distance) / distance**2
            gradient += coeff * 2 * (x - y)

        return gradient

    def Likelihood(self, x, neighbors):
        coeffs = 0.
        likelihood = 0.
        for neighbor, distance in neighbors.items():
            y = neighbor.cartesian_x
            likelihood += (np.dot(x - y, x - y) - distance)**2 / distance**2

        return likelihood

    def Update(self):
        x0 = np.zeros_like(self.cartesian_x)
        x = optimize.fmin_cg(self.Likelihood,
                             x0,
                             args=(self.neighbors,),
                             disp=False)
        print str(self)
        print x
        self.cartesian_x = x

        likelihood = self.Likelihood(x, self.neighbors)
        print likelihood

        return likelihood


class Model:
    def __init__(self):
        self.latlong_to_coordinates = {}
        self.points = {}
        self.addresses = {}
        self.Read("data/addresses_all.csv", "data/durations_all.csv")

    def Read(self, addresses_filename, durations_filename):
        f = open(addresses_filename, "r")
        reader = csv.reader(f)
        a = lambda x: 2 * round(x / 2, 3)
        for lat, lng, address in reader:
            try:
                lat = float(lat)
                lng = float(lng)
            except:
                continue
            
            key = ("%.3f" % a(lat), "%.3f" % a(lng))
            self.addresses[key] = address
        f.close()

        f = open(durations_filename, "r")
        reader = csv.reader(f)
        
        for row in reader:
            try:
                (slat, slng, elat, elng, duration) = row
                slat = float(slat)
                slng = float(slng)
                elat = float(elat)
                elng = float(elng)
                duration = float(duration)
            except:
                print "Failed to process row: %s" % str(row)
                continue

            key_start = ("%.3f" % slat, "%.3f" % slng)
            if key not in self.points:
                self.points[key_start] = Point(slat, slng)

            key_end = ("%.3f" % elat, "%.3f" % elng)
            if key_end not in self.points:
                self.points[key_end] = Point(elat, elng)

            p_start = self.points[key_start]
            p_end = self.points[key_end]

            p_start.AddNeighbor(p_end, duration)
            p_end.AddNeighbor(p_start, duration)

            p_start.address = self.addresses.get(key_start, "")
            p_end.address = self.addresses.get(key_end, "")

        f.close()

    def Write(self):
        out_file = open("results.csv", "w")
        writer = csv.writer(out_file)
        writer.writerow([
            "lat", "lng", "cart_lat", "car_lng", "address" ])
        for (lat, lng), point in self.points.items():
            writer.writerow([
                lat, lng, "%.3f" % point.cartesian_x[0], "%.3f" % point.cartesian_x[1],
                point.address ])

        out_file.close()
        
    
    def Infer(self):
        likelihood = 10000000.
        last_likelihood = 10000000.
        converged = False
        while not converged:
            likelihood = 0.
            for key, point in self.points.items():
                likelihood += point.Update()

            converged = (last_likelihood - likelihood) < 0.01
            last_likelihood = likelihood
            
    
if __name__ == '__main__':
    model = Model()
    model.Infer()
    model.Save()

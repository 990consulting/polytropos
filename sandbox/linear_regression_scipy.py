import numpy
import scipy.stats

years = numpy.asarray(range(2010, 2014))
weights = numpy.asarray([190.7, 188.3, 192.4, 185.2])

lm = scipy.stats.linregress(years, weights)
slope, intercept, r_value, p_value, std_err = lm
print(lm)

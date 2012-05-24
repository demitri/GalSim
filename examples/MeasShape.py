#!/usr/bin/env python
"""
This script can be run from the command-line to carry out PSF correction on images, parallel to
MeasMoments.py

It takes arguments from the command line, i.e.
MeasShape.py gal_image_file PSF_image_file [sky_var shear_estimator sky_level sky_level_PSF]
where the ones in brackets are optional:
gal_image_file: A file containing a PSF-convolved galaxy image
PSF_image_file: A file containing the PSF image
[sky_var]: An optional estimate for the sky variance in the image (only necessary if you want an
           estimate of the error on the PSF-corrected shapes).
[shear_estimator]: The shear estimator to use, either REGAUSS, LINEAR, BJ, or KSB (default: REGAUSS) 
[sky_level]: If the image contains a non-zero sky level, it must be specified
[sky_level_PSF]: If the PSF image contains a non-zero sky level, it must be specified

Results will be printed to stdout:
Status (0 = success), PSF-corrected e1, e2, measurement type ('e' = ellipticity, 'g' = shear),
resolution factor, sigma_e, Gaussian sigma of the observed galaxy in pixels, total flux in the best-fit
elliptical Gaussian

Here we use the e1 = (Mxx - Myy)/(Mxx + Myy) and e2 = 2*Mxy/(Mxx + Mxy) definition of ellipticity.

"""

import sys
import os

# This machinery lets us run Python examples even though they aren't positioned properly to find
# galsim as a package in the current directory. 
try:
    import galsim
except ImportError:
    path, filename = os.path.split(__file__)
    sys.path.append(os.path.abspath(os.path.join(path, "..")))
    import galsim

# process arguments
numArg = len(sys.argv)-1
if (numArg < 2 or numArg > 6):
    raise RuntimeError("Wrong number of command-line arguments: should be in the range 2...6!")
gal_image_file = sys.argv[1]
PSF_image_file = sys.argv[2]
sky_var = 0.0
shear_estimator = "REGAUSS"
sky_level = 0.0
sky_level_psf = 0.0
if (numArg >= 3):
    sky_var = float(sys.argv[3])
if (numArg >= 4):
    shear_estimator = sys.argv[4]
if (numArg >= 5):
    sky_level = float(sys.argv[5])
if (numArg == 6):
    sky_level_psf = float(sys.argv[6])

# prepare and read in inputs
gal_image = galsim.fits.read(gal_image_file)
if sky_level != 0.:
    gal_image -= sky_level
PSF_image = galsim.fits.read(PSF_image_file)
if sky_level_psf != 0.:
    PSF_image -= sky_level_psf

# measure shape, output results
result = galsim.EstimateShearHSM(gal_image, PSF_image, sky_var = sky_var,
                                 shear_est = shear_estimator)
meas_type = 'e'
if (shear_estimator == "KSB"):
    meas_type = 'g'
print '%d   %12.6f   %12.6f   %c  %12.6f   %12.6f   %12.6f   %12.6f   %12.6f' % \
    (result.correction_status, result.corrected_shape.getE1(), result.corrected_shape.getE2(),
     meas_type, 1.0, result.resolution_factor, result.corrected_shape_err, result.moments_sigma,
     result.moments_amp)

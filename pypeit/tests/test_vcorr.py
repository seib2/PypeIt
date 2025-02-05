"""
Module to run tests on arvcorr
"""
import numpy as np
import pytest

from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units

from linetools import utils as ltu

from pypeit.core import wave
from pypeit import specobjs
from pypeit.tests.tstutils import dummy_fitstbl

mjd = 57783.269661
RA = '07:06:23.45'
DEC = '+30:20:50.5'
hdr_equ = 2000.
lon = 155.47833            # Longitude of the telescope (NOTE: West should correspond to positive longitudes)
lat = 19.82833             # Latitude of the telescope
alt = 4160.0               # Elevation of the telescope (in m)


@pytest.fixture
def fitstbl():
    return dummy_fitstbl()


def test_geovelocity():
    """ Test the full geomotion velocity calculation
    """
    loc = (lon * units.deg, lat * units.deg, alt * units.m,)

    radec = SkyCoord(RA, DEC, unit=(units.hourangle, units.deg), frame='icrs')
    obstime = Time(mjd, format='mjd', scale='utc', location=loc)

    corrhelio = wave.geomotion_velocity(obstime, radec, frame="heliocentric")
    corrbary = wave.geomotion_velocity(obstime, radec, frame="barycentric")

    # IDL
    # vhel = x_keckhelio(106.59770833333332, 30.34736111111111, 2000., jd=2457783.769661)
    #    vrotate = -0.25490532
    assert np.isclose(corrhelio, -12.49764005490221, rtol=1e-5)
    assert np.isclose(corrbary, -12.510015817405023, rtol=1e-5)


def test_geocorrect(fitstbl):
    """
    """
    # Spectrograph
    # (KBW) Had to change this to keck to match the telecope parameters,
    # then just changed to use definitions above directly.
#    spectrograph = load_spectrograph('keck_lris_blue')

    # Specobjs (wrap in a list to mimic a slit)
    sobj_list = specobjs.dummy_specobj((2048,2048), extraction=True)
    specObjs = specobjs.SpecObjs(sobj_list)
    scidx = 5
    obstime = Time(fitstbl['mjd'][scidx], format='mjd')#'%Y-%m-%dT%H:%M:%S.%f')
    maskslits = np.array([False]*specObjs.nobj)
    radec = ltu.radec_to_coord((fitstbl["ra"][scidx], fitstbl["dec"][scidx]))

    helio, hel_corr = wave.geomotion_correct(specObjs, radec, obstime, maskslits,
                                               lon, lat, alt, 'heliocentric')
    assert np.isclose(helio, -9.17461338, rtol=1e-5)  # Checked against x_keckhelio
    #assert np.isclose(helio, -9.3344957, rtol=1e-5)  # Original
    assert np.isclose(specObjs[0].boxcar['WAVE'][0].value, 3999.877589008, rtol=1e-8)


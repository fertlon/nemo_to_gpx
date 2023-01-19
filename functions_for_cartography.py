from math import sin, cos, acos, pi


def dms2dd(d, m, s):
    """Convertit un angle "degrés minutes secondes" en "degrés décimaux"
    """
    return d + m / 60 + s / 3600


def dd2dms(dd):
    """Convertit un angle "degrés décimaux" en "degrés minutes secondes"
    """
    d = int(dd)
    x = (dd - d) * 60
    m = int(x)
    s = (x - m) * 60
    return d, m, s


def deg2rad(dd):
    """Convertit un angle "degrés décimaux" en "radians"
    """
    return dd / 180 * pi


def rad2deg(rd):
    """Convertit un angle "radians" en "degrés décimaux"
    """
    return rd / pi * 180


def distance_gps_harvesine(lat_a, lon_a, lat_b, lon_b):
    """Retourne la distance en mètres entre les 2 points A et B connus grâce à
       leurs coordonnées GPS (en degrés décimaux). Méthode de Harvesine.
    """
    # cooordonnées GPS en radians du 1er point
    lat_a = deg2rad(lat_a)
    lon_a = deg2rad(lon_a)

    # cooordonnées GPS en radians du 2ème point
    lat_b = deg2rad(lat_b)
    lon_b = deg2rad(lon_b)

    # Rayon de la terre en mètres (sphère IAG-GRS80)
    earth_radius = 6378137
    # angle en radians entre les 2 points
    val = sin(lat_a) * sin(lat_b) + cos(lat_a) * cos(lat_b) * cos(lon_b - lon_a)
    if val > 1:
        s = 0
    else:
        s = acos(val)
    # distance entre les 2 points, comptée sur un arc de grand cercle
    return s * earth_radius

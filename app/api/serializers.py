from host import models
from rest_framework import serializers


class TransientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transient
        fields = ['name', 'ra_deg', 'dec_deg', 'public_timestamp', 'redshift',
                  'milkyway_dust_reddening', 'spectroscopic_class',
                  'photometric_class']


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Host
        fields = ['name', 'ra_deg', 'dec_deg', 'redshift',
                  'milkyway_dust_reddening']


class ApertureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Aperture
        fields = ['orientation_deg', 'semi_major_axis_arcsec',
                  'semi_minor_axis_arcsec']

def serialize_blast_science_data(transient) -> dict:
    """
    Serializes all data associated with a transient
    """
    transient_data = TransientSerializer(transient).data
    host_data = HostSerializer(transient.host).data

    for filter in models.Filter.objects.all():
        pass

    transient_data = {'transient_' + name: value for name, value in transient_data.items()}
    host_data = {'host_' + name: value for name, value in host_data.items()}
    return {**transient_data, **host_data}







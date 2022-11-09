from dataclasses import dataclass

from host import models
from rest_framework import serializers


class CutoutField(serializers.RelatedField):
    def to_representation(self, value):
        return value.filter.name


class TransientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transient
        fields = [
            "name",
            "ra_deg",
            "dec_deg",
            "public_timestamp",
            "redshift",
            "milkyway_dust_reddening",
            "spectroscopic_class",
            "photometric_class",
            "processing_status",
        ]


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Host
        fields = ["name", "ra_deg", "dec_deg", "redshift", "milkyway_dust_reddening"]


class ApertureSerializer(serializers.ModelSerializer):
    cutout = CutoutField(read_only=True)

    class Meta:
        model = models.Aperture
        fields = [
            "ra_deg",
            "dec_deg",
            "orientation_deg",
            "semi_major_axis_arcsec",
            "semi_minor_axis_arcsec",
            "cutout",
        ]


class AperturePhotometrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AperturePhotometry
        fields = ["flux", "flux_error", "magnitude", "magnitude_error","is_validated"]


class SEDFittingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SEDFittingResult
        fields = [
            "log_mass_16",
            "log_mass_50",
            "log_mass_84",
            "log_sfr_16",
            "log_sfr_50",
            "log_sfr_84",
            "log_ssfr_16",
            "log_ssfr_50",
            "log_sfr_84",
            "log_ssfr_16",
            "log_ssfr_50",
            "log_ssfr_84",
            "log_age_16",
            "log_age_50",
            "log_age_84",
            "log_tau_16",
            "log_tau_50",
            "log_tau_84",
        ]

from dataclasses import dataclass

from host import models
from rest_framework import serializers
import datetime

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
    def validate_name(self, value):
        """
        Check that the name is a string
        """
        if type(value) != str:
            raise serializers.ValidationError("Transient name is not a string")
        return value

    def validate_ra_deg(self, value):
        """
        Check that ra is valid
        """
        if type(value) != float:
            raise serializers.ValidationError("Transient ra is not a float")
        if value < 0.0 or value > 360.0:
            raise serializers.ValidationError("Transient ra is not between 0 and 360 degrees")
        return value

    def validate_dec_deg(self, value):
        """
        Check that dec is valid
        """
        if type(value) != float:
            raise serializers.ValidationError("Transient dec is not a float")
        if value < -90.0 or value > 90.0:
            raise serializers.ValidationError("Transient dec is not between -90 and 90 degrees")
        return value

    def validate_public_timestamp(self, value):
        """
        Check if public time stamp is valid
        """
        if type(value) != str:
            raise serializers.ValidationError("Transient public timestamp is not a string")

        try:
            format_string = '%Y-%m-%dT%H:%M:%S.%f%z'
            datetime.datetime.strptime(value, format_string)
        except ValueError:
            raise serializers.ValidationError("Transient public timestamp is not in iso UTC format e.g. 2014-01-01T00:00:00.588Z")

        return value







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
        fields = ["flux", "flux_error", "magnitude", "magnitude_error"]


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

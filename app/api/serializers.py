import datetime
from dataclasses import dataclass

import api.validation as validation
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

    def validate_ra_deg(self, value):
        """
        Check that ra is valid
        """
        if validation.ra_deg_valid(value):
            return value
        else:
            raise serializers.ValidationError("Transient RA is not valid")

    def validate_dec_deg(self, value):
        """
        Check that dec is valid
        """
        if validation.dec_deg_valid(value):
            return value
        else:
            raise serializers.ValidationError("Transient DEC is not valid")

    def create(self, validated_data):
        """Creates new transient"""
        science_payload = validated_data["science_payload"]
        data_model_component = validated_data["data_model_component"]
        data = self.science_payload_to_model_data(science_payload, data_model_component)
        return models.Transient.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Updates existing transient"""
        for field in self.fields:
            setattr(
                instance, field, validated_data.get(field, getattr(instance, field))
            )
        instance.tasks_initialized = "True"
        instance.save()
        return instance

    def science_payload_to_model_data(self, science_payload: dict, data_model_component) -> dict:
        """Converts science payload to data to be passed to the model"""
        all_column_names = science_payload.keys()
        columns = [name for name in all_column_names if name.startswith(data_model_component.prefix)]
        records = [name.replace(data_model_component.prefix, "") for name in columns]
        return {record: science_payload[column] for column, record in zip(columns, records)}


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Host
        fields = ["name", "ra_deg", "dec_deg", "redshift", "milkyway_dust_reddening"]

    def validate_ra_deg(self, value):
        """
        Check that ra is valid
        """
        if validation.ra_deg_valid(value):
            return value
        else:
            raise serializers.ValidationError("Host RA is not valid")

    def validate_dec_deg(self, value):
        """
        Check that dec is valid
        """
        if validation.dec_deg_valid(value):
            return value
        else:
            raise serializers.ValidationError("Host DEC is not valid")

    def create(self, validated_data):
        """Creates new Host with transient"""
        transient = validated_data["transient"]
        del validated_data["transient"]
        host = models.Host.objects.create(**validated_data)
        transient.host = host
        transient.save()
        return host

    def update(self, instance, validated_data):
        """Updates existing transient"""
        transient = validated_data["transient"]
        del validated_data["transient"]
        transient.host = instance
        transient.save()
        for field in self.fields:
            setattr(
                instance, field, validated_data.get(field, getattr(instance, field))
            )
        instance.save()
        return instance

    def science_payload_to_model_data(self, science_payload: dict, data_model_component) -> dict:
        """Converts science payload to data to be passed to the model"""
        all_column_names = science_payload.keys()
        columns = [name for name in all_column_names if name.startswith(data_model_component.prefix)]
        records = [name.replace(data_model_component.prefix, "") for name in columns]
        data = {record: science_payload[column] for column, record in zip(columns, records)}
        data["transient"] = models.Transient.objects.get(name__exact=science_payload["transient_name"])
        return data



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

    def create(self, validated_data):
        """Creates new Aperture with transient"""
        validated_data["name"] = (
            validated_data["transient"].name + "_" + validated_data["type"]
        )
        aperture = models.Aperture.objects.create(**validated_data)
        return aperture

    def update(self, instance, validated_data):
        """Updates existing Aperture"""
        validated_data["name"] = (
            validated_data["transient"].name + "_" + validated_data["type"]
        )
        for field in self.fields + ["name"]:
            setattr(
                instance, field, validated_data.get(field, getattr(instance, field))
            )
        instance.save()
        return instance

    def validate_ra_deg(self, value):
        """
        Check that ra is valid
        """
        if validation.ra_deg_valid(value):
            return value
        else:
            raise serializers.ValidationError("Aperture RA is not valid")

    def science_payload_to_model_data(self, science_payload: dict, data_model_component) -> dict:
        """Converts science payload to data to be passed to the model"""
        all_column_names = science_payload.keys()
        columns = [name for name in all_column_names if name.startswith(data_model_component.prefix)]
        records = [name.replace(data_model_component.prefix, "") for name in columns]
        data = {record: science_payload[column] for column, record in zip(columns, records)}

        transient_name = science_payload["transient_name"]
        aperture_type, _ = data_model_component.prefix.split("_")

        data["transient"] = models.Transient.objects.get(name__exact=transient_name)
        data["type"] = aperture_type
        data["name"] = f"{transient_name}_{aperture_type}"

        if data["cutout"] is not None:
            data["cutout"] = models.Cutout.objects.get(transient__name__exact=transient_name,
                                                       filter_name__exact=data["cutout"])
        return data

    def validate_dec_deg(self, value):
        """
        Check that dec is valid
        """
        if validation.dec_deg_valid(value):
            return value
        else:
            raise serializers.ValidationError("Aperture DEC is not valid")


class AperturePhotometrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AperturePhotometry
        fields = ["flux", "flux_error", "magnitude", "magnitude_error"]

    def create(self, validated_data):
        """Creates new Aperture with transient"""
        aperture = models.AperturePhotometry.objects.create(**validated_data)
        return aperture

    def update(self, instance, validated_data):
        """Updates existing Aperture"""
        for field in self.fields:
            setattr(
                instance, field, validated_data.get(field, getattr(instance, field))
            )
        instance.save()
        return instance

    def science_payload_to_model_data(self, science_payload: dict, data_model_component) -> dict:
        """Converts science payload to data to be passed to the model"""
        all_column_names = science_payload.keys()
        columns = [name for name in all_column_names if name.startswith(data_model_component.prefix)]
        records = [name.replace(data_model_component.prefix, "") for name in columns]
        data = {record: science_payload[column] for column, record in zip(columns, records)}

        transient_name = science_payload["transient_name"]
        prefix = data_model_component.prefix.split("_")
        aperture_type, filter_name = prefix[0], f"{prefix[2]}_{prefix[3]}"

        data["transient"] = models.Transient.objects.get(name__exact=transient_name)
        data["aperture"] = models.Aperture.objects.get(type__exact=aperture_type, transient__name__exact=transient_name)
        data["filter"] = models.Filter.objects.get(name__exact=filter_name)
        return data



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

    def science_payload_to_model_data(self, science_payload: dict, data_model_component) -> dict:
        """Converts science payload to data to be passed to the model"""
        all_column_names = science_payload.keys()
        columns = [name for name in all_column_names if name.startswith(data_model_component.prefix)]
        records = [name.replace(data_model_component.prefix, "") for name in columns]
        data = {record: science_payload[column] for column, record in zip(columns, records)}

        transient_name = science_payload["transient_name"]
        aperture_type = data_model_component.prefix.split("_")[0]

        data["transient"] = models.Transient.objects.get(name__exact=transient_name)
        data["aperture"] = models.Aperture.objects.get(type__exact=aperture_type, transient__name__exact=transient_name)
        return data

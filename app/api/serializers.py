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
            "orientation_deg",
            "semi_major_axis_arcsec",
            "semi_minor_axis_arcsec",
            "type",
            "cutout",
        ]


class AperturePhotometrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AperturePhotometry
        fields = ["flux", "flux_error", "magnitude", "magnitude_error"]


def serialize_blast_science_data(transient_name) -> dict:
    """
    Serializes all data associated with a transient
    """
    serializers = [
        TransientSerializer,
        HostSerializer,
        ApertureSerializer,
        ApertureSerializer,
    ]
    prefixes = ["transient_", "host_", "local_aperture_", "global_aperture_"]
    queries = [
        {"name__exact": transient_name},
        {"transient__name__exact": transient_name},
        {"transient__name__exact": transient_name, "type__exact": "local"},
        {"transient__name__exact": transient_name, "type__exact": "global"},
    ]
    blast_models = [models.Transient, models.Host, models.Aperture, models.Aperture]

    for filter in models.Filter.objects.all():
        for type in ["local", "global"]:
            serializers.append(AperturePhotometrySerializer)
            blast_models.append(models.AperturePhotometry)
            queries.append(
                {
                    "transient__name__exact": transient_name,
                    "filter__name__exact": filter.name,
                    "aperture__type__exact": type,
                }
            )
            prefixes.append(f"{type}_{filter.name}_")

    science_payload = {}

    for model, serializer, prefix, query in zip(
        blast_models, serializers, prefixes, queries
    ):
        try:
            object = model.objects.get(**query)
            object_data = serializer(object).data
            object_dict = {prefix + name: value for name, value in object_data.items()}

        except:
            object_dict = {prefix + name: None for name in serializer().fields}

        science_payload = {**science_payload, **object_dict}

    return science_payload

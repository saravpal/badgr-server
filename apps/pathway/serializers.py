# Created by wiggins@concentricsky.com on 3/30/16.
from collections import OrderedDict

from django.conf import settings
from django.core.urlresolvers import reverse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from issuer.models import Issuer
from pathway.models import Pathway, PathwayElement


class PathwayListSerializer(serializers.Serializer):

    def to_representation(self, pathways):
        pathways_serializer = PathwaySerializer(pathways, many=True, context=self.context)
        return OrderedDict([
            ("@context", "https://badgr.io/public/contexts/pathways"),
            ("@type", "IssuerPathwayList"),
            ("pathways", pathways_serializer.data),
        ])


class PathwaySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=254, write_only=True)
    description = serializers.CharField(write_only=True)

    def to_representation(self, instance):
        issuer_slug = self.context.get('issuer_slug', None)
        if not issuer_slug:
            raise ValidationError("Invalid issuer_slug")

        representation = OrderedDict([
            ("@id", settings.HTTP_ORIGIN+reverse('pathway_detail', kwargs={'issuer_slug': issuer_slug, 'pathway_slug': instance.slug})),
            ('slug', instance.slug),
            ('name', instance.cached_root_element.name),
            ('description', instance.cached_root_element.description),
        ])
        return representation

    def create(self, validated_data, **kwargs):
        issuer_slug = self.context.get('issuer_slug', None)
        if not issuer_slug:
            raise ValidationError("Could not determine issuer")
        try:
            issuer = Issuer.cached.get(slug=issuer_slug)
        except Issuer.DoesNotExist:
            raise ValidationError("Could not determine issuer")

        name = validated_data.get('name')

        pathway = Pathway(issuer=issuer)
        pathway.save(name_hint=name)
        root_element = PathwayElement(
            pathway=pathway,
            parent_element=None,
            name=name,
            description=validated_data.get('description'),
        )
        root_element.save()
        pathway.root_element = root_element
        pathway.save()
        return pathway

    def update(self, instance, validated_data):
        pass





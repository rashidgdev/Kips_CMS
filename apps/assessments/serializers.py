from rest_framework import serializers

from .models import Assessment, AssessmentCategory


class AssessmentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentCategory
        fields = ['id', 'name', 'default_weight_percent']


class AssessmentSerializer(serializers.ModelSerializer):
    category_label = serializers.StringRelatedField(source='category', read_only=True)

    class Meta:
        model = Assessment
        fields = [
            'id', 'course_offering', 'category', 'category_label', 'title', 'total_marks',
            'weight_percent', 'date',
        ]
        read_only_fields = ['course_offering']

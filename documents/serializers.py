# documents/serializers.py
from rest_framework import serializers
from .models import DocumentTemplate, DocumentGenerationTask

class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'template_type', 'description', 'is_active']

class DocumentGenerationTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentGenerationTask
        fields = ['id', 'topic', 'requirements', 'status', 'word_count', 
                 'charts_count', 'formulas_count', 'created_at', 'completed_at']
        read_only_fields = ['id', 'status', 'word_count', 'charts_count', 
                          'formulas_count', 'created_at', 'completed_at']

class DocumentGenerationRequestSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=500)
    template_id = serializers.IntegerField(required=False)
    word_count = serializers.IntegerField(default=2000, min_value=500, max_value=10000)
    include_charts = serializers.BooleanField(default=True)
    include_formulas = serializers.BooleanField(default=True)
    language = serializers.ChoiceField(choices=[('zh', 'Chinese'), ('en', 'English')], default='zh')
    
    def validate_template_id(self, value):
        if value and not DocumentTemplate.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid template ID")
        return value
"""
Serializers for files APIs
"""
from rest_framework import serializers

from core.models import File


def validate_file_extension(file_extension):
    allowed_extensions = ['pdf', 'dxf', 'xlsx', 'xls', 'txt', 'png',
                          'jpg', 'jpeg', 'rar', 'zip', 'doc', 'docx',
                          'igs', 'step', 'stp', 'stl']
    if file_extension in allowed_extensions:
        return True
    else:
        return False    


class FilesUploadSerializer(serializers.ModelSerializer):
    """Serializer for upload file"""
    file = serializers.ListField(
        child=serializers.FileField(
            max_length=100000,
            allow_empty_file=False,
            use_url=False
        ))

    class Meta:
        model = File
        fields = '__all__'

        extra_kwargs = {
            'name': {'required': False},
        }

    def create(self, validated_data):
        project = validated_data['project']
        user = validated_data['user']
        destiny = validated_data['destiny']
        file = validated_data.pop('file')
        file_list = []

        for file in file:
            file_name_str = str(file).lower()
            file_split = file_name_str.split('.')
            file_extension = file_split[-1]
            if validate_file_extension(file_extension):
                file_obj = File.objects.create(
                    file=file, project=project, user=user,
                    destiny=destiny, name=file.name
                )
                fileurl = f'{file_obj.file.url}'
                file_list.append(fileurl)
            else:
                raise serializers.ValidationError('Wrong file format')
        return file_list
    

class FileSerializer(serializers.ModelSerializer):
    """Serializer for file"""
    class Meta:
        model = File
        fields = '__all__'
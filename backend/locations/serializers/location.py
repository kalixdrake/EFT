from rest_framework import serializers

from locations.models import Address, Department, Municipality


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name')


class MunicipalitySerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True,
    )

    class Meta:
        model = Municipality
        fields = ('id', 'name', 'department', 'department_id')


class MunicipalityNestedSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Municipality
        fields = ('id', 'name', 'department')


class AddressSerializer(serializers.ModelSerializer):
    municipality = MunicipalityNestedSerializer(read_only=True)

    class Meta:
        model = Address
        fields = ('id', 'line', 'postal_code', 'label', 'is_default', 'municipality', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class AddressWriteSerializer(serializers.ModelSerializer):
    municipality_id = serializers.PrimaryKeyRelatedField(
        queryset=Municipality.objects.all(),
        source='municipality',
    )

    class Meta:
        model = Address
        fields = ('id', 'line', 'postal_code', 'label', 'is_default', 'municipality_id')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

from rest_framework import serializers
from apiTransacciones.models.categorias_model import Categoria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
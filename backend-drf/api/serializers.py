from rest_framework import serializers




class StockPredictionSerializer(serializers.Serializer):
    ticker = serializers.CharField(max_length=50)
    days = serializers.IntegerField(min_value=1, max_value=365, required=True)
    
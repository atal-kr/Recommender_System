from rest_framework import serializers


class Results(object):
    """"it is used to format the response."""
    def __init__(self,code,status,message="",extra_field=None):
        self.status=status
        self.code=code
        self.message=message
        self.extra_field=extra_field
    def to_json_dict(self):
        """Convert to a dict for serializing to JSON."""
        result={"code": self.code, "status": self.status,"message":self.message}
        if self.extra_field:
            result.update(self.extra_field)
        return result
    def serialize(self):
        return ResultSerializer(self.to_json_dict()).data

class ResultSerializer(serializers.Serializer):
        """it is used to serialize Response."""
        code=serializers.IntegerField()
        status=serializers.CharField(max_length=10)
        message=serializers.CharField(max_length=100)
        results=serializers.SerializerMethodField()
        def get_results(self,obj):
                return   obj.get('results',[])



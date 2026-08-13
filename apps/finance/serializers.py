from rest_framework import serializers

from .models import Challan, ChallanLine, FeeCategory, FeeStructure, Payment, StudentFeeItem


class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = ['id', 'name']


class FeeStructureSerializer(serializers.ModelSerializer):
    program_label = serializers.StringRelatedField(source='program', read_only=True)
    category_label = serializers.StringRelatedField(source='category', read_only=True)

    class Meta:
        model = FeeStructure
        fields = ['id', 'program', 'program_label', 'category', 'category_label', 'amount', 'is_recurring']


class StudentFeeItemSerializer(serializers.ModelSerializer):
    category_label = serializers.StringRelatedField(source='category', read_only=True)
    semester_label = serializers.StringRelatedField(source='semester', read_only=True)

    class Meta:
        model = StudentFeeItem
        fields = ['id', 'category', 'category_label', 'semester', 'semester_label', 'amount_due', 'due_date']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'fee_item', 'challan', 'amount_paid', 'payment_date', 'payment_method']


class ChallanLineSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(source='fee_item.category', read_only=True)

    class Meta:
        model = ChallanLine
        fields = ['id', 'fee_item', 'category', 'amount']


class ChallanSerializer(serializers.ModelSerializer):
    student_label = serializers.StringRelatedField(source='student', read_only=True)
    semester_label = serializers.StringRelatedField(source='semester', read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Challan
        fields = [
            'id', 'challan_number', 'student', 'student_label', 'semester', 'semester_label',
            'issue_date', 'due_date', 'total_amount', 'is_cancelled', 'status',
        ]

    def get_status(self, obj):
        from .services import get_challan_status
        return get_challan_status(obj)

from django.contrib import admin

from .models import (Discount, FeeItem, GradeFeeItem, Payment, PaymentItem,
                     StudentDiscount, StudentFeeAssignment)

# After creationg a grade fee item we need to assign that to all students, I need to do this right now ---


admin.site.register(Discount)
admin.site.register(StudentDiscount)
admin.site.register(FeeItem)
admin.site.register(GradeFeeItem)
admin.site.register(StudentFeeAssignment)
admin.site.register(Payment)
admin.site.register(PaymentItem)

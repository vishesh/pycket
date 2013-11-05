from rpython.tool.pairtype import extendabletype
from rpython.rlib.rbigint import rbigint
from rpython.rlib import rarithmetic
from pycket import values

def make_int(w_value):
    if isinstance(w_value, values.W_Bignum):
        try:
            num = w_value.value.toint()
        except OverflowError:
            pass
        else:
            return values.W_Fixnum(num)
    return w_value

class __extend__(values.W_Number):
    def arith_sqrt(self):
        ## FIXME: wrong for Scheme numbers
        return self.arith_pow(values.W_Flonum(0.5))

class __extend__(values.W_Fixnum):
    # ------------------ addition ------------------ 
    def arith_add(self, other):
        return other.arith_add_number(self.value)

    def arith_add_number(self, other_num):
        try:
            res = rarithmetic.ovfcheck(other_num + self.value)
        except OverflowError:
            return self.arith_add_bigint(rbigint.fromint(other_num))
        return values.W_Fixnum(res)

    def arith_add_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.add(rbigint.fromint(self.value))))
    def arith_add_float(self, other_float):
        return values.W_Flonum(other_float + float(self.value))

    def arith_unaryadd(self):
        return self

    # ------------------ subtraction ------------------ 
    def arith_sub(self, other):
        return other.arith_sub_number(self.value)

    def arith_sub_number(self, other_num):
        try:
            res = rarithmetic.ovfcheck(other_num - self.value)
        except OverflowError:
            return self.arith_sub_bigint(rbigint.fromint(other_num))
        return values.W_Fixnum(res)

    def arith_sub_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.sub(rbigint.fromint(self.value))))

    def arith_sub_float(self, other_float):
        return values.W_Flonum(other_float - float(self.value))

    def arith_unarysub(self):
        try:
            res = rarithmetic.ovfcheck(-self.value)
        except OverflowError:
            return values.W_Bignum(rbigint.fromint(self.value).neg())
        return values.W_Fixnum(res)


    # ------------------ multiplication ------------------ 
    def arith_mul(self, other):
        if not self.value: return self
        return other.arith_mul_number(self.value)

    def arith_mul_number(self, other_num):
        if not self.value: return self
        try:
            res = rarithmetic.ovfcheck(other_num * self.value)
        except OverflowError:
            return self.arith_mul_bigint(rbigint.fromint(other_num))
        return values.W_Fixnum(res)

    def arith_mul_bigint(self, other_value):
        if not self.value: return self
        return make_int(values.W_Bignum(other_value.mul(rbigint.fromint(self.value))))

    def arith_mul_float(self, other_float):
        if not self.value: return self
        return values.W_Flonum(other_float * float(self.value))

    # ------------------ division ------------------ 
    def arith_div(self, other):
        return other.arith_div_number(self.value)

    def arith_div_number(self, other_num):
        if self.value == 0:
            error.throw_evaluation_error("zero_divisor")
        try:
            res = rarithmetic.ovfcheck(other_num / self.value)
        except OverflowError:
            return self.arith_div_bigint(rbigint.fromint(other_num))
        return values.W_Fixnum(res)

    def arith_div_bigint(self, other_value):
        if self.value == 0:
            error.throw_evaluation_error("zero_divisor")
        return make_int(values.W_Bignum(other_value.div(rbigint.fromint(self.value))))

    def arith_div_float(self, other_float):
        if self.value == 0:
            error.throw_evaluation_error("zero_divisor")
        return values.W_Flonum(other_float / float(self.value))

    def arith_floordiv(self, other):
        return other.arith_floordiv_number(self.value)

    def arith_floordiv_number(self, other_num):
        if self.value == 0:
            error.throw_evaluation_error("zero_divisor")
        try:
            res = rarithmetic.ovfcheck(other_num // self.value)
        except OverflowError:
            return self.arith_floordiv_bigint(rbigint.fromint(other_num))
        return values.W_Fixnum(res)

    def arith_floordiv_bigint(self, other_value):
        if self.value == 0:
            error.throw_evaluation_error("zero_divisor")
        return make_int(values.W_Bignum(other_value.floordiv(rbigint.fromint(self.value))))

    def arith_floordiv_float(self, other_float):
        error.throw_type_error("integer", other_float)


    # ------------------ power ------------------ 
    def arith_pow(self, other):
        return other.arith_pow_number(self.value)

    def arith_pow_number(self, other_num):
        try:
            res = ovfcheck_float_to_int(math.pow(other_num, self.value))
        except OverflowError:
            return self.arith_pow_bigint(rbigint.fromint(other_num))
        return values.W_Fixnum(res)

    def arith_pow_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.pow(rbigint.fromint(self.value))))

    def arith_pow_float(self, other_float):
        return values.W_Flonum(math.pow(other_float, float(self.value)))

    # ------------------ shift right ------------------ 
    def arith_shr(self, other):
        return other.arith_shr_number(self.value)

    def arith_shr_number(self, other_num):
        return values.W_Fixnum(other_num >> self.value)

    def arith_shr_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.rshift(self.value)))

    # ------------------ shift left ------------------ 
    def arith_shl(self, other):
        return other.arith_shl_number(self.value)

    def arith_shl_number(self, other_num):
        return values.W_Fixnum(intmask(other_num << self.value))

    def arith_shl_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.lshift(self.value)))

    # ------------------ or ------------------ 
    def arith_or(self, other):
        return other.arith_or_number(self.value)

    def arith_or_number(self, other_num):
        return values.W_Fixnum(other_num | self.value)

    def arith_or_bigint(self, other_value):
        return make_int(values.W_Bignum(rbigint.fromint(self.value).or_(other_value)))

    # ------------------ and ------------------ 
    def arith_and(self, other):
        return other.arith_and_number(self.value)

    def arith_and_number(self, other_num):
        return values.W_Fixnum(other_num & self.value)

    def arith_and_bigint(self, other_value):
        return make_int(values.W_Bignum(rbigint.fromint(self.value).and_(other_value)))

    # ------------------ xor ------------------ 
    def arith_xor(self, other):
        return other.arith_xor_number(self.value)

    def arith_xor_number(self, other_num):
        return values.W_Fixnum(other_num ^ self.value)

    def arith_xor_bigint(self, other_value):
        return make_int(values.W_Bignum(rbigint.fromint(self.value).xor(other_value)))

    # ------------------ mod ------------------ 
    def arith_mod(self, other):
        return other.arith_mod_number(self.value)

    def arith_mod_number(self, other_num):
        if self.value == 0:
            error.throw_evaluation_error("zero_divisor")
        return values.W_Fixnum(other_num % self.value)

    def arith_mod_bigint(self, other_value):
        if self.value == 0:
            error.throw_evaluation_error("zero_divisor")
        return make_int(values.W_Bignum(other_value.mod(rbigint.fromint(self.value))))

    # ------------------ inversion ------------------
    def arith_not(self):
        return values.W_Fixnum(~self.value)


    # ------------------ abs ------------------
    def arith_abs(self):
        if self.value >= 0:
            return self
        return values.W_Fixnum(0).arith_sub(self)

    # ------------------ max ------------------
    def arith_max(self, other):
        return other.arith_max_number(self.value)

    def arith_max_number(self, other_num):
        return values.W_Fixnum(max(other_num, self.value))

    def arith_max_bigint(self, other_value):
        self_value = rbigint.fromint(self.value)
        if self_value.lt(other_value):
            return make_int(values.W_Bignum(other_value))
        return make_int(values.W_Bignum(self_value))

    def arith_max_float(self, other_float):
        return values.W_Flonum(max(other_float, float(self.value)))

    # ------------------ min ------------------
    def arith_min(self, other):
        return other.arith_min_number(self.value)

    def arith_min_number(self, other_num):
        return values.W_Fixnum(min(other_num, self.value))

    def arith_min_bigint(self, other_value):
        self_value = rbigint.fromint(self.value)
        if self_value.lt(other_value):
            return make_int(values.W_Bignum(self_value))
        return make_int(values.W_Bignum(other_value))

    def arith_min_float(self, other_float):
        return values.W_Flonum(min(other_float, float(self.value)))

    # ------------------ miscellanous ------------------
    def arith_round(self):
        return self

    def arith_floor(self):
        return self

    def arith_ceiling(self):
        return self

    def arith_float_fractional_part(self):
        return values.W_Fixnum(0)

    def arith_float_integer_part(self):
        return self


class __extend__(values.W_Flonum):    
    # ------------------ addition ------------------ 
    def arith_add(self, other):
        return other.arith_add_float(self.value)

    def arith_add_number(self, other_num):
        return values.W_Flonum(float(other_num) + self.value)

    def arith_add_bigint(self, other_value):
        return values.W_Flonum(other_value.tofloat() + self.value)

    def arith_add_float(self, other_float):
        return values.W_Flonum(other_float + self.value)

    def arith_unaryadd(self):
        return self

    # ------------------ subtraction ------------------ 
    def arith_sub(self, other):
        return other.arith_sub_float(self.value)

    def arith_sub_number(self, other_num):
        return values.W_Flonum(float(other_num) - self.value)

    def arith_sub_bigint(self, other_value):
        return values.W_Flonum(other_value.tofloat() - self.value)

    def arith_sub_float(self, other_float):
        return values.W_Flonum(other_float - self.value)

    def arith_unarysub(self):
        return values.W_Flonum(-self.value)

    # ------------------ multiplication ------------------ 
    def arith_mul(self, other):
        return other.arith_mul_float(self.value)

    def arith_mul_number(self, other_num):
        return values.W_Flonum(float(other_num) * self.value)

    def arith_mul_bigint(self, other_value):
        return values.W_Flonum(other_value.tofloat() * self.value)

    def arith_mul_float(self, other_float):
        return values.W_Flonum(other_float * self.value)

    # ------------------ division ------------------ 
    def arith_div(self, other):
        return other.arith_div_float(self.value)

    def arith_div_number(self, other_num):
        if self.value == 0.0:
            error.throw_evaluation_error("zero_divisor")
        return values.W_Flonum(float(other_num) / self.value)

    def arith_div_bigint(self, other_value):
        if self.value == 0.0:
            error.throw_evaluation_error("zero_divisor")
        return values.W_Flonum(other_value.tofloat() / self.value)

    def arith_div_float(self, other_float):
        if self.value == 0.0:
            error.throw_evaluation_error("zero_divisor")
        return values.W_Flonum(other_float / self.value)

    def arith_floordiv(self, other_float):
        error.throw_type_error("integer", self)
    def arith_floordiv_number(self, other_num):
        error.throw_type_error("integer", self)
    def arith_floordiv_bigint(self, other_value):
        error.throw_type_error("integer", self)
    def arith_floordiv_float(self, other_float):
        error.throw_type_error("integer", other_float)

    # ------------------ power ------------------ 
    def arith_pow(self, other):
        return other.arith_pow_float(self.value)

    def arith_pow_number(self, other_num):
        return values.W_Flonum(math.pow(float(other_num), self.value))

    def arith_pow_bigint(self, other_value):
        return values.W_Flonum(math.pow(other_value.tofloat(), self.value))

    def arith_pow_float(self, other_float):
        return values.W_Flonum(math.pow(other_float, self.value))

    # ------------------ abs ------------------ 
    def arith_abs(self):
        return values.W_Flonum(abs(self.value))

    # ------------------ max ------------------ 
    def arith_max(self, other):
        return other.arith_max_float(self.value)

    def arith_max_number(self, other_num):
        return values.W_Flonum(max(float(other_num), self.value))

    def arith_max_bigint(self, other_value):
        return values.W_Flonum(max(other_value.tofloat(), self.value))

    def arith_max_float(self, other_float):
        return values.W_Flonum(max(other_float, self.value))
    
    # ------------------ min ------------------ 
    def arith_min(self, other):
        return other.arith_min_float(self.value)

    def arith_min_number(self, other_num):
        return values.W_Flonum(min(float(other_num), self.value))

    def arith_min_bigint(self, other_value):
        return values.W_Flonum(min(other_value.tofloat(), self.value))

    def arith_min_float(self, other_float):
        return values.W_Flonum(min(other_float, self.value))

    # ------------------ miscellanous ------------------
    def arith_round(self):
        fval = self.value
        if fval >= 0:
            factor = 1
        else:
            factor = -1

        fval = fval * factor
        try:
            val = ovfcheck_float_to_int(math.floor(fval + 0.5) * factor)
        except OverflowError:
            return values.W_Bignum(rbigint.fromfloat(math.floor(self.value + 0.5) * factor))
        return values.W_Fixnum(val)

    def arith_floor(self):
        try:
            val = ovfcheck_float_to_int(math.floor(self.value))
        except OverflowError:
            return values.W_Bignum(rbigint.fromfloat(math.floor(self.value)))
        return values.W_Fixnum(val)

    def arith_ceiling(self):
        try:
            val = ovfcheck_float_to_int(math.ceil(self.value))
        except OverflowError:
            return values.W_Bignum(rbigint.fromfloat(math.ceil(self.value)))
        return values.W_Fixnum(val)

    def arith_float_fractional_part(self):
        try:
            val = ovfcheck_float_to_int(self.value)
        except OverflowError:
            val = rbigint.fromfloat(self.value).tofloat()
        return values.W_Flonum(float(self.value - val))

    def arith_float_integer_part(self):
        try:
            val = ovfcheck_float_to_int(self.value)
        except OverflowError:
            return values.W_Bignum(rbigint.fromfloat(self.value))
        return values.W_Fixnum(val)


class __extend__(values.W_Bignum):
    # ------------------ addition ------------------ 
    def arith_add(self, other):
        return other.arith_add_bigint(self.value)

    def arith_add_number(self, other_num):
        return make_int(values.W_Bignum(rbigint.fromint(other_num).add(self.value)))

    def arith_add_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.add(self.value)))

    def arith_add_float(self, other_float):
        return values.W_Flonum(other_float + self.value.tofloat())

    def arith_unaryadd(self):
        return self

    # ------------------ subtraction ------------------ 
    def arith_sub(self, other):
        return other.arith_sub_bigint(self.value)

    def arith_sub_number(self, other_num):
        return make_int(values.W_Bignum(rbigint.fromint(other_num).sub(self.value)))

    def arith_sub_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.sub(self.value)))

    def arith_sub_float(self, other_float):
        return values.W_Flonum(other_float - self.value.tofloat())

    def arith_unarysub(self):
        return values.W_Bignum(self.value.neg())

    # ------------------ multiplication ------------------ 
    def arith_mul(self, other):
        return other.arith_mul_bigint(self.value)

    def arith_mul_number(self, other_num):
        return make_int(values.W_Bignum(rbigint.fromint(other_num).mul(self.value)))

    def arith_mul_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.mul(self.value)))

    def arith_mul_float(self, other_float):
        return values.W_Flonum(other_float * self.value.tofloat())

    # ------------------ division ------------------ 
    def arith_div(self, other):
        return other.arith_div_bigint(self.value)

    def arith_div_number(self, other_num):
        return make_int(values.W_Bignum(rbigint.fromint(other_num).div(self.value)))

    def arith_div_bigint(self, other_value):
        try:
            return make_int(values.W_Bignum(other_value.div(self.value)))
        except ZeroDivisionError:
            error.throw_evaluation_error("zero_divisor")

    def arith_div_float(self, other_float):
        return values.W_Flonum(other_float / self.value.tofloat())

    def arith_floordiv(self, other):
        return other.arith_floordiv_bigint(self.value)

    def arith_floordiv_number(self, other_num):
        return make_int(values.W_Bignum(rbigint.fromint(other_num).div(self.value)))

    def arith_floordiv_bigint(self, other_value):
        try:
            return make_int(values.W_Bignum(other_value.div(self.value)))
        except ZeroDivisionError:
            error.throw_evaluation_error("zero_divisor")

    def arith_floordiv_float(self, other_float):
        error.throw_type_error("integer", other_float)
    # ------------------ power ------------------
    def arith_pow(self, other):
        return other.arith_pow_bigint(self.value)

    def arith_pow_number(self, other_num):
        return make_int(values.W_Bignum(rbigint.fromint(other_num).pow(self.value)))

    def arith_pow_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.pow(self.value)))

    def arith_pow_float(self, other_float):
        return values.W_Flonum(math.pow(other_float, self.value.tofloat()))

    # ------------------ shift right ------------------ 
    def arith_shr(self, other):
        return other.arith_shr_bigint(self.value)

    def arith_shr_number(self, other_num):
        try:
            num = self.value.toint()
        except OverflowError:
            # XXX raise a Prolog-level error!
            raise ValueError('Right operand too big')
        return values.W_Fixnum(other_num >> num)

    def arith_shr_bigint(self, other_value):
        try:
            num = self.value.toint()
        except OverflowError:
            # XXX raise a Prolog-level error!
            raise ValueError('Right operand too big')
        return make_int(values.W_Bignum(other_value.rshift(num)))

    # ------------------ shift left ------------------ 
    def arith_shl(self, other):
        return other.arith_shl_bigint(self.value)

    def arith_shl_number(self, other_num):
        try:
            num = self.value.toint()
        except OverflowError:
            # XXX raise a Prolog-level error!
            raise ValueError('Right operand too big')
        else:
            return make_int(values.W_Bignum(rbigint.fromint(other_num).lshift(num)))

    def arith_shl_bigint(self, other_value):
        try:
            num = self.value.toint()
        except OverflowError:
            # XXX raise a Prolog-level error!
            raise ValueError('Right operand too big')
        return make_int(values.W_Bignum(other_value.lshift(num)))

    # ------------------ or ------------------ 
    def arith_or(self, other):
        return other.arith_or_bigint(self.value)

    def arith_or_number(self, other_num):
        return make_int(values.W_Bignum(rbigint.fromint(other_num).or_(self.value)))

    def arith_or_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.or_(self.value)))

    # ------------------ and ------------------ 
    def arith_and(self, other):
        return other.arith_and_bigint(self.value)

    def arith_and_number(self, other_num):
        return make_int(values.W_Bignum(rbigint.fromint(other_num).and_(self.value)))

    def arith_and_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.and_(self.value)))

    # ------------------ xor ------------------ 
    def arith_xor(self, other):
        return other.arith_xor_bigint(self.value)

    def arith_xor_number(self, other_num):
        return make_int(values.W_Bignum(rbigint.fromint(other_num).xor(self.value)))

    def arith_xor_bigint(self, other_value):
        return make_int(values.W_Bignum(other_value.xor(self.value)))

    # ------------------ mod ------------------ 
    def arith_mod(self, other):
        return other.arith_mod_bigint(self.value)

    def arith_mod_number(self, other_num):
        try:
            return make_int(values.W_Bignum(rbigint.fromint(other_num).mod(self.value)))
        except ZeroDivisionError:
            error.throw_evaluation_error("zero_divisor")

    def arith_mod_bigint(self, other_value):
        try:
            return make_int(values.W_Bignum(other_value.mod(self.value)))
        except ZeroDivisionError:
            error.throw_evaluation_error("zero_divisor")

    # ------------------ inversion ------------------ 
    def arith_not(self):
        return make_int(values.W_Bignum(self.value.invert()))


    # ------------------ abs ------------------
    def arith_abs(self):
        return make_int(values.W_Bignum(self.value.abs()))


    # ------------------ max ------------------
    def arith_max(self, other):
        return other.arith_max_bigint(self.value)

    def arith_max_number(self, other_num):
        other_value = rbigint.fromint(other_num)
        if other_value.lt(self.value):
            return make_int(values.W_Bignum(self.value))
        return make_int(values.W_Bignum(other_value))

    def arith_max_bigint(self, other_value):
        if other_value.lt(self.value):
            return make_int(values.W_Bignum(self.value))
        return make_int(values.W_Bignum(other_value))

    def arith_max_float(self, other_float):
        return values.W_Flonum(max(other_float, self.value.tofloat()))

    # ------------------ min ------------------
    def arith_min(self, other):
        return other.arith_min_bigint(self.value)

    def arith_min_number(self, other_num):
        other_value = rbigint.fromint(other_num)
        if other_value.lt(self.value):
            return make_int(values.W_Bignum(other_value))
        return make_int(values.W_Bignum(self.value))

    def arith_min_bigint(self, other_value):
        if other_value.lt(self.value):
            return make_int(values.W_Bignum(other_value))
        return make_int(values.W_Bignum(self.value))

    def arith_min_float(self, other_float):
        return values.W_Flonum(min(other_float, self.value.tofloat()))

    # ------------------ miscellanous ------------------
    def arith_round(self):
        return make_int(self)

    def arith_floor(self):
        return make_int(self)

    def arith_ceiling(self):
        return make_int(self)

    def arith_arith_fractional_part(self):
        return values.W_Fixnum(0)

    def arith_arith_integer_part(self):
        return make_int(self)
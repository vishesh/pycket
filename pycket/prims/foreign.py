#! /usr/bin/env python
# -*- coding: utf-8 -*-

# XXX: This whole module is wrong

import sys

from pycket              import values
from pycket.error        import SchemeException
from pycket.foreign      import W_CType, W_PrimitiveCType, W_DerivedCType
from pycket.prims.expose import default, expose, expose_val, procedure
from rpython.rlib        import jit, unroll

if sys.maxint == 2147483647:    # 32-bit
    POINTER_SIZE = 4
else:                           # 64-bit
    POINTER_SIZE = 8

PRIMITIVE_CTYPES = [
    ("int8"          , 1            ) ,
    ("int16"         , 2            ) ,
    ("int32"         , 4            ) ,
    ("int64"         , 8            ) ,
    ("uint8"         , 1            ) ,
    ("uint16"        , 2            ) ,
    ("uint32"        , 4            ) ,
    ("uint64"        , 8            ) ,
    ("bytes"         , POINTER_SIZE ) ,
    ("path"          , POINTER_SIZE ) ,
    ("pointer"       , POINTER_SIZE ) ,
    ("fpointer"      , POINTER_SIZE ) ,
    ("string/utf-16" , POINTER_SIZE ) ,
    ("gcpointer"     , POINTER_SIZE ) ,
    ]

sym = values.W_Symbol.make

# Best effort
COMPILER_SIZEOF = unroll.unrolling_iterable([
    (sym("int"    ) , POINTER_SIZE ) ,
    (sym("char"   ) , 1            ) ,
    (sym("short"  ) , 1            ) ,
    (sym("long"   ) , POINTER_SIZE ) ,
    (sym("*"      ) , POINTER_SIZE ) ,
    (sym("void"   ) , 1            ) ,
    (sym("float"  ) , 4            ) ,
    (sym("double" ) , 8            ) ,
    ])

del sym

for name, size in PRIMITIVE_CTYPES:
    ctype   = W_PrimitiveCType(name, size)
    exposed = W_DerivedCType(ctype, values.w_false, values.w_false)
    expose_val("_" + name, ctype)

@expose("make-ctype", [W_CType, values.W_Object, values.W_Object])
def make_c_type(ctype, rtc, ctr):
    if rtc is not values.w_false and not rtc.iscallable():
        raise SchemeException("make-ctype: expected (or/c #f procedure) in argument 1 got %s" %
                              rtc.tostring())
    if ctr is not values.w_false and not ctr.iscallable():
        raise SchemeException("make-ctype: expected (or/c #f procedure) in argument 2 got %s" %
                              ctr.tostring())
    return W_DerivedCType(ctype, rtc, ctr)

@jit.elidable
def _compiler_sizeof(ctype):
    if ctype.is_proper_list():
        acc = 0
        while ctype is not values.w_null:
            car, ctype = ctype.car(), ctype.cdr()
            if not isinstance(car, values.W_Symbol):
                break
            acc += _compiler_sizeof(car)
        else:
            return acc

    if not isinstance(ctype, values.W_Symbol):
        msg = ("compiler-sizeof: expected (or/c symbol? (listof symbol?)) in argument 0 got %s" %
               ctype.tostring())
        raise SchemeException(msg)

    for sym, size in COMPILER_SIZEOF:
        if ctype is sym:
            return size
    raise SchemeException("compiler-sizeof: %s is not a valid C type" % ctype.tostring())

@expose("compiler-sizeof", [values.W_Object])
def compiler_sizeof(obj):
    return values.W_Fixnum(_compiler_sizeof(obj))

@expose("make-stubborn-will-executor", [])
def make_stub_will_executor():
    return values.w_false

@expose("ctype-sizeof", [W_CType])
def ctype_sizeof(ctype):
    return values.W_Fixnum(ctype.sizeof())

@expose("ctype?", [W_CType])
def ctype(c):
    return values.W_Bool.make(isinstance(c, W_CType))

@expose("ffi-lib?", [values.W_Object])
def ffi_lib(o):
    # Naturally, since we don't have ffi values
    return values.w_false

@expose("ffi-lib")
def ffi_lib(args):
    return values.w_false

@expose("malloc")
def malloc(args):
    return values.W_CPointer()

@expose("ptr-ref")
def ptr_ref(args):
    return values.w_void

@expose("ptr-set!")
def ptr_set(args):
    return values.w_void

@expose("cpointer-gcable?")
def cp_gcable(args):
    return values.w_false

@expose("ffi-obj")
def ffi_obj(args):
    return values.W_CPointer()

@expose("ctype-basetype", [values.W_Object])
def ctype_basetype(ctype):
    if ctype is values.w_false:
        return values.w_false
    if not isinstance(ctype, W_CType):
        msg = ("ctype-basetype: expected (or/c ctype? #f) in argument 0 got %s" %
               ctype.tostring())
        raise SchemeException(msg)
    while isinstance(ctype, W_DerivedCType):
        ctype = ctype.ctype
    assert isinstance(ctype, W_PrimitiveCType)
    return ctype


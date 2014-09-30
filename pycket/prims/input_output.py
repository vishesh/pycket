#! /usr/bin/env python
# -*- coding: utf-8 -*-
from rpython.rlib.rsre import rsre_re as re
from rpython.rlib import jit
from rpython.rlib             import streamio as sio
from rpython.rlib.rbigint     import rbigint
from rpython.rlib.rstring     import ParseStringError, ParseStringOverflowError
from rpython.rlib.rarithmetic import string_to_int
from pycket.cont import continuation, loop_label, call_cont
from pycket                   import values
from pycket.error             import SchemeException
from pycket.prims.expose      import default, expose, expose_val
import os

class Token(object):
    def __init__(self, v):
        self.val = v

class NumberToken(Token): pass
class StringToken(Token): pass
class SymbolToken(Token): pass
class BooleanToken(Token): pass
class LParenToken(Token): pass
class RParenToken(Token): pass
class LVecToken(Token): pass
class RVecToken(Token): pass

def read_number_or_id(f, init):
    sofar = init
    while True:
        (count, c) = f.peek()
        if c == "":
            break
        c = c[0]
        if c.isalnum():
            sofar = sofar + f.read(1)
        else:
            break
    try:
        return NumberToken(values.W_Fixnum.make(string_to_int(sofar)))
    except ParseStringOverflowError:
        val = rbigint.fromdecimalstr(sofar)
        return NumberToken(values.W_Bignum(val))
    except ParseStringError:
        try:
            return NumberToken(values.W_Flonum.make(float(sofar)))
        except:
            return SymbolToken(values.W_Symbol.make(sofar))

def read_token(f):
    while True:
        c = f.read(1) # FIXME: unicode
        if c in [" ", "\n", "\t"]:
            continue
        if c in ["(", "[", "{"]:
            return LParenToken(values.W_String.make(c))
        if c in [")", "]", "}"]:
            return RParenToken(values.W_String.make(c))
        if c.isalnum():
            return read_number_or_id(f, c)
        if c == "#":
            c2 = f.read(1)
            if c2 == "t":
                return BooleanToken(values.w_true)
            if c2 == "f":
                return BooleanToken(values.w_false)
            if c2 in ["(", "[", "{"]:
                return LVecToken(values.W_String.make(c2))
            raise SchemeException("bad token in read: %s" % c2)
        raise SchemeException("bad token in read: %s" % c)

@expose("read", [default(values.W_InputPort, None)], simple=False)
def read(port, env, cont):
    from pycket.interpreter import return_value
    if port is None:
        port = current_out_param.get(cont)
    assert isinstance(port, values.W_InputPort)
    stream = port.file
    token = read_token(stream)
    if isinstance(token, NumberToken):
        v = token.val
    elif isinstance(token, StringToken):
        v = token.val
    elif isinstance(token, SymbolToken):
        v = token.val
    elif isinstance(token, BooleanToken):
        v = token.val
    else:
        v = values.w_false # fail!
    return return_value(v, env, cont)

@expose("read-line", [default(values.W_InputPort, None)], simple=False)
def read(port, env, cont):
    from pycket.interpreter import return_value
    if port is None:
        port = current_in_param.get(cont)
    assert isinstance(port, values.W_InputPort)
    stream = port.file
    return return_value(values.W_String(stream.readline()), env, cont)

text_sym   = values.W_Symbol.make("text")
binary_sym = values.W_Symbol.make("binary")
none_sym   = values.W_Symbol.make("none")
error_sym  = values.W_Symbol.make("error")

@expose("open-input-file", [values.W_String,
                            default(values.W_Symbol, binary_sym),
                            default(values.W_Symbol, none_sym)])
def open_input_file(str, mode, mod_mode):
    m = "r" if mode is text_sym else "rb"
    return open_infile(str, m)

@expose("open-output-file", [values.W_String,
                             default(values.W_Symbol, binary_sym),
                             default(values.W_Symbol, error_sym)])
def open_output_file(str, mode, exists):
    m = "w" if mode is text_sym else "wb"
    return open_outfile(str, m)

@expose("port-closed?", [values.W_Port])
def port_closedp(p):
    return values.W_Bool.make(p.closed)

@expose("eof-object?", [values.W_Object])
def eofp(e):
    return values.W_Bool.make(e is values.eof_object)

@continuation
def close_cont(port, env, cont, vals):
    from pycket.interpreter import return_multi_vals
    port.file.close()
    return return_multi_vals(vals, env, cont)    

def open_infile(str, mode):
    s = str.value
    return values.W_FileInputPort(sio.open_file_as_stream(s, mode=mode))

def open_outfile(str, mode):
    s = str.value
    return values.W_FileOutputPort(sio.open_file_as_stream(s, mode=mode))

@expose("call-with-input-file", [values.W_String, values.W_Object], simple=False)
def call_with_input_file(s, proc, env, cont):
    port = open_infile(s, "rb")
    return proc.call([port], env, close_cont(port, env, cont))

@expose("call-with-output-file", [values.W_String, values.W_Object], simple=False)
def call_with_output_file(s, proc, env, cont):
    port = open_outfile(s, "wb")
    return proc.call([port], env, close_cont(port, env, cont))

@expose("with-input-from-file", [values.W_String, values.W_Object], simple=False)
def with_input_from_file(s, proc, env, cont):
    from pycket.prims.general      import call_with_extended_paramz
    port = open_infile(s, "rb")
    return call_with_extended_paramz(proc, [], [current_in_param], [port], 
                                     env, close_cont(port, env, cont))

@expose("with-output-to-file", [values.W_String, values.W_Object], simple=False)
def with_output_to_file(s, proc, env, cont):
    from pycket.prims.general      import call_with_extended_paramz
    port = open_outfile(s, "wb")
    return call_with_extended_paramz(proc, [], [current_out_param], [port], 
                                     env, close_cont(port, env, cont))


@expose("print-struct", [default(values.W_Object, None)])
def do_print_struct(on):
    return values.w_true

@expose("display", [values.W_Object, default(values.W_OutputPort, None)], simple=False)
def display(datum, out, env, cont):
    return do_print(datum.tostring(), out, env, cont)

@expose("newline", [default(values.W_OutputPort, None)], simple=False)
def newline(out, env, cont):
    return do_print("\n", out, env, cont)

@expose("write", [values.W_Object, default(values.W_OutputPort, None)], simple=False)
def write(o, p, env, cont):
    return do_print(o.tostring(), p, env, cont)

@expose("print", [values.W_Object, default(values.W_OutputPort, None)], simple=False)
def _print(o, p, env, cont):
    return do_print(o.tostring(), p, env, cont)

def do_print(str, port, env, cont):
    if port is None:
        port = current_out_param.get(cont)
    port.write(str)
    return return_void(env, cont)

format_dict = {
    '~n': '\n',
    '~%': '\n',
    '~a': None,
    '~e': None,
    '~s': None
}
format_regex = re.compile("|".join(format_dict.keys()))

@jit.unroll_safe
def format(form, v):
    from rpython.rlib.rstring import StringBuilder
    text = form.value
    result = StringBuilder()
    pos = 0
    for match in format_regex.finditer(text):
        match_start = match.start()
        assert match_start >= 0
        result.append(text[pos : match_start])
        val = format_dict[match.group()]
        if val is None:
            val, v = v[0].tostring(), v[1:]
        result.append(val)
        pos = match.end()
        assert pos >= 0
    result.append(text[pos:])
    return result.build()

@expose("printf")
def printf(args):
    if not args:
        raise SchemeException("printf expected at least one argument, got 0")
    fmt = args[0]
    if not isinstance(fmt, values.W_String):
        raise SchemeException("printf expected a format string, got something else")
    fmt = fmt.value
    vals = args[1:]
    i = 0
    j = 0
    while i < len(fmt):
        if fmt[i] == '~':
            if i+1 == len(fmt):
                raise SchemeException("bad format string")
            s = fmt[i+1]
            if s == 'a' or s == 'v' or s == 's':
                # print a value
                # FIXME: different format chars
                if j >= len(vals):
                    raise SchemeException("not enough arguments for format string")
                os.write(1, vals[j].tostring())
                j += 1
            elif s == 'n':
                os.write(1,"\n") # newline
            else:
                raise SchemeException("unexpected format character")
            i += 2
        else:
            os.write(1,fmt[i])
            i += 1


@expose("format")
def do_format(args):
    form, v = args[0], args[1:]
    assert isinstance(form, values.W_String)
    return values.W_String(format(form, v))

@expose("fprintf", simple=False)
def do_fprintf(args, env, cont):
    out, form, v = args[0], args[1], args[2:]
    assert isinstance(out, values.W_OutputPort)
    assert isinstance(form, values.W_String)
    out.write(format(form, v))
    return return_void(env, cont)

# Why is this different than format/fprintf?
# @expose("printf", simple=False)
# def do_printf(args, env, cont):
#     port = current_out_param.get(cont)
#     return do_fprintf([port] + args, env, cont)

def return_void(env, cont):
    from pycket.interpreter import return_value
    return return_value(values.w_void, env, cont)

@expose("flush-output", [default(values.W_OutputPort, None)], simple=False)
def flush_output(port, env, cont):
    if port is None:
        port = current_out_param.get(cont)
    port.flush()
    return return_void(env, cont)
    

def cur_print_proc(args, env, cont):
    from pycket.interpreter import return_value
    v, = args
    port = current_out_param.get(cont)
    if v is not values.w_void:
        port.write(v.tostring())
        port.write("\n")
    return return_void(env, cont)

standard_printer = values.W_Prim("current-print", cur_print_proc)

@expose("open-output-string", [])
def open_output_string():
    return values.W_StringOutputPort()

@expose("port-display-handler", [values.W_OutputPort])
def port_display_handler(p):
    return standard_printer

@expose("port-write-handler", [values.W_OutputPort])
def port_write_handler(p):
    return standard_printer

current_print_param = values.W_Parameter(standard_printer)
expose_val("current-print", current_print_param)

stdout_port = values.W_FileOutputPort(sio.fdopen_as_stream(1, "wb"))
stdin_port = values.W_FileInputPort(sio.fdopen_as_stream(0, "rb"))
current_out_param = values.W_Parameter(stdout_port)
current_in_param = values.W_Parameter(stdin_port)
expose_val("current-output-port", current_out_param)
expose_val("current-input-port", current_in_param)
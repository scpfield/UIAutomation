import sys
import builtins
import os
import io
import operator
import gc
import ctypes
import tracemalloc
import linecache
import inspect
import json
import random
import traceback
import msvcrt
from functools import wraps
from colorama import Fore, Back, Style, init as colorama_init


def getattr(Object, Name, Default = None):
    try:
        return builtins.getattr(Object, Name, Default)
    except BaseException as e:
        return False
    ...


def GetShortArgs(*Args):

    NewArgs = ()
    if Args:
        ArgsList = list(Args)
        for Idx, Value in enumerate(ArgsList):
            ValueStr = str(Value)
            if len(ValueStr) > 512:
                NewArgs = NewArgs + ( ValueStr[:512] + " (TRUNCATED)", )
                #builtins.print(NewArgs)
            else:
                NewArgs = NewArgs + ( ValueStr, )
    
    Args = NewArgs
    return Args

    
def print( *Args, sep=' ', end='\n', file=None, flush=False, Decorate=True ):
    
    if len(Args) == 0:
        Decorate = False
        
    if Decorate:

        FrameInfo = list( inspect.stack() + inspect.trace() )[1]
        
        # FrameFunction    = str( FrameInfo.function )        
        FrameFunction    = str( sys._getframe(1).f_code.co_qualname)
        FrameLineNumber  = str( FrameInfo.lineno )
        FrameClassName   = None
        Color            = None
        FrameValue       = None

        if not FrameValue:
            FrameValue = FrameInfo[0].f_locals.get( 'cls' )
            if FrameValue: 
                FrameClassName = str( FrameValue.__name__ ) + '.'
                Color = Fore.YELLOW
        
        if not FrameValue:
            FrameValue = FrameInfo[0].f_locals.get( 'self' )
            if FrameValue:
                FrameClassName = str( FrameValue.__class__.__name__ ) + '.'
                Color = Fore.CYAN

        if not FrameValue:
            FrameValue = FrameInfo[0].f_locals.get( '__name__' )
            if FrameValue:
                FrameClassName = str( FrameValue ) + '.'
                Color = Fore.BLUE
    
        if not FrameValue:
            CodeObj = FrameInfo[0].f_code
            Referrers = gc.get_referrers(CodeObj)
            FrameClassName = str(Referrers[0]).split('.')[0].split(' ')[1]+'.'
            Color = Fore.MAGENTA
            
        Caller = f'{FrameClassName}{FrameFunction}:{FrameLineNumber}'
        
        Output  = Style.BRIGHT + Fore.WHITE + Back.BLACK + '['    + Style.RESET_ALL
        Output += Style.BRIGHT + Color      + Back.BLACK + Caller + Style.RESET_ALL
        Output += Style.BRIGHT + Fore.WHITE + Back.BLACK + ']'    + Style.RESET_ALL
    
        NewArgs = tuple()
        
        #if Args:
        #    ArgsList = list(Args)
        #    for Idx, Value in enumerate(ArgsList):
        #        ValueStr = str(Value)
        #        if len(ValueStr) > 128:
        #            NewArgs = NewArgs + ( ValueStr[:128], )
        #            builtins.print(NewArgs)
        #        else:
        #            NewArgs = NewArgs + ( ValueStr, )
        
        Args = GetShortArgs(*Args)
        #builtins.print(NewArgs)
        #Pause()
        #if len(Args[0]) > 128:
        #    Args[0] = Args[0][:128]
        
        builtins.print(f'{Output}', *Args, sep=sep, end=end, file=file, flush=flush )
        
    else:
        builtins.print(*Args, sep=sep, end=end, file=file, flush=flush)
        
        
def GetCallerClass():

    FrameInfo = list( inspect.stack() + inspect.trace() )[1]
        
    FrameFunction    = str( FrameInfo.function )        
    FrameLineNumber  = str( FrameInfo.lineno )
    
    CodeObj = FrameInfo[0].f_code
    Referrers = gc.get_referrers(CodeObj)
    FrameClassName = str(Referrers[0]).split('.')[0].split(' ')[1]+'.'    

    return FrameClassName, FrameFunction, FrameLineNumber
    
    
def GetExceptionInfo(e):
    ExceptionType, ExceptionValue, ExceptionTrace = sys.exc_info()
    ExceptionInfo =  str( f'Type: {ExceptionType}\n' +
                          f'Value: {ExceptionValue}\n' +
                          f'Trace: {ExceptionTrace}')
    
    builtins.print(ExceptionInfo)
    traceback.print_tb(ExceptionTrace)
    Pause()
    return(ExceptionInfo)

    
def RandomString(Length=10):
    RandBytes = bytearray(Length)
    for x in range(Length):
        RandBytes[x] = random.randrange(65,91)
    return(RandBytes.decode().replace(" ", "_").lower())

def Pause(Text="Pausing"):
    builtins.print(Text)
    key = msvcrt.getch()
    if key == b'q':
        quit()

def Stack( Print = True, Exclude = 0 ):

    OutputStr = ''
    
    for Idx, FrameInfo in enumerate( list( inspect.stack() + inspect.trace() ), 1):
       
        #if Idx < Exclude:
        #    continue
            
        FrameClassName   = None
        FrameLineNumber  = str( FrameInfo.lineno )
        FrameFunction    = str( FrameInfo.function )
        FrameCodeContext = ''.join( map( str.strip,
                            FrameInfo.code_context ))
        FrameValue = None
            
        if not FrameValue:
            FrameValue = FrameInfo[0].f_locals.get( 'cls' )
            if FrameValue: 
                FrameClassName = str( FrameValue.__name__ ) + '.'

        if not FrameValue:
            FrameValue = FrameInfo[0].f_locals.get( 'self' )
            if FrameValue:
                FrameClassName = str( FrameValue.__class__.__name__ ) + '.'

        if not FrameValue:
            FrameValue = FrameInfo[0].f_locals.get( '__name__' )
            if FrameValue:
                FrameClassName = str( FrameValue ) + '.'
    
        if not FrameValue:
            CodeObj = FrameInfo[0].f_code
            Referrers = gc.get_referrers(CodeObj)
            FrameClassName = str(Referrers[0]).split('.')[0].split(' ')[1]+'.'
            
        OutputStr +=    str( f'Class: {FrameClassName}, '    +
                             f'Function: {FrameFunction}, '  +
                             f'Line: {FrameLineNumber}, '    + 
                             f'Code: {FrameCodeContext}\n' )
        
    if Print:
        builtins.print( 'Stack:' )
        builtins.print(OutputStr)
    return OutputStr
    
    ...

def ResponseInfo(Response):
    builtins.print()
    builtins.print(f'Request URL      : {Response.request.url}' )
    builtins.print(f'Request Path     : {Response.request.path_url}' )
    builtins.print(f'Request Method   : {Response.request.method}' )
    builtins.print(f'Request Headers  : {Response.request.headers}')
    builtins.print(f'Request Body     : {Response.request.body}')
    builtins.print(f'Response Code    : {Response.status_code}' )
    builtins.print(f'Response Reason  : {Response.reason}' )
    builtins.print(f'Response Time    : {Response.elapsed.total_seconds() * 1000} ms')
    builtins.print(f'Response Headers : {Response.headers}' )
    builtins.print(f'Response Text    : {Response.text}' )
...


def IsInt( Obj ):
    try:
        IntObj = int( Obj )
    except:
        return False
    else:
        return True
        
def IsFloat( Obj ):
    try:
        IntObj = float( Obj )
    except:
        return False
    else:
        return True

    
def Info(Obj, Depth = 0, Static = False):
    
    builtins.print()
    builtins.print("Type = " + str(type(Obj)))
    #builtins.print("Class = " + str(Obj.__class__))
    #builtins.print(str(inspect.getclasstree( [Obj.__class__] ) ))
    builtins.print()

    
    def PrintArgs(FullArgSpec):
        args = FullArgSpec.args
        varargs = FullArgSpec.varargs
        varkw = FullArgSpec.varkw
        defaults = FullArgSpec.defaults
        kwonlyargs = FullArgSpec.kwonlyargs
        kwonlydefaults = FullArgSpec.kwonlydefaults
        annotations = FullArgSpec.annotations
        builtins.print('(', end='')
        if args: builtins.print('args = ' + str(args), end='')
        if defaults: builtins.print(', defaults = ' + str(defaults), end='')
        if varargs: builtins.print(', varargs = ' + str(varargs), end='')
        if varkw: builtins.print(', varkw = ' + str(varkw), end='')
        if kwonlyargs: builtins.print(', kwonlyargs = ' + str(kwonlyargs), end='')
        if kwonlydefaults: builtins.print(', kwonlydefaults = ' + str(kwonlydefaults), end='')
        if annotations: builtins.print(', annotations = ' + str(annotations), end='')    
        builtins.print(')')
    
    def Dump(Obj, Level = 0, Static = False):
        
        if Level > Depth:
            return            
        
        MemberList = []
        
        if Static:
            MemberList = inspect.getmembers_static(Obj)
        else:
            MemberList = inspect.getmembers(Obj)
        
        MaxMemberLength = 0
        
        for Member in MemberList:
            if len(Member[0]) > MaxMemberLength:
                MaxMemberLength = len(Member[0])
                
        for Member in MemberList:
           
            Name  = str(Member[0])
            Value = Member[1]
            Indent = '     ' * Level
            builtins.print(Indent + '.' + Name, end = '')
            NextIndent = (' ' * ((MaxMemberLength + 5) - len(Name)))
            builtins.print(NextIndent, end='')
            #builtins.print(type(Value))
            
            builtins.print(f'Type = {type(Value).__name__}', end=' ')
            
            if (inspect.ismodule( Value )):
                builtins.print()
                continue

            if (inspect.isclass( Value )):
                builtins.print(f'( Value = {Value})')
                builtins.print(inspect.getmro(Value))
                continue
            
            if (inspect.ismethod( Value )):
                try:
                    PrintArgs(inspect.getfullargspec(Value))
                except:
                    builtins.print(str(Value))
                continue

            if (inspect.isfunction( Value )):
                try:
                    PrintArgs(inspect.getfullargspec(Value))
                except:
                  builtins.print(str(Value))
                continue
                
            if (inspect.isgeneratorfunction( Value )):
                builtins.print()
                continue
            
            if (inspect.isgenerator( Value )):
                builtins.print()
                continue
                
            if (inspect.iscoroutinefunction( Value )):
                builtins.print()
                continue        

            if (inspect.iscoroutine( Value )):
                builtins.print()
                continue

            if (inspect.isawaitable( Value )):
                builtins.print()
                continue 

            if (inspect.isasyncgenfunction( Value )):
                builtins.print()
                continue                  

            if (inspect.isasyncgen( Value )):
                builtins.print()
                continue

            if (inspect.istraceback( Value )):
                builtins.print()
                continue

            if (inspect.isframe( Value )):
                builtins.print()
                continue

            if (inspect.iscode( Value )):
                builtins.print()
                continue

            if (inspect.isbuiltin( Value )):
                builtins.print()
                continue

            if (inspect.ismethodwrapper( Value )):
                try:
                    PrintArgs(inspect.getfullargspec(Value))
                except:
                    builtins.print(str(Value))
                continue

            if (inspect.isroutine( Value )):
                try:
                    PrintArgs(inspect.getfullargspec(Value))
                except:
                    builtins.print(str(Value))
                continue
                
            if (inspect.isabstract( Value )):
                builtins.print()
                continue

            if (inspect.ismethoddescriptor( Value )):
                builtins.print()
                continue
            
            if (inspect.isdatadescriptor( Value )):
                builtins.print()
                continue

            if (inspect.isgetsetdescriptor( Value )):
                builtins.print()
                continue

            if (inspect.ismemberdescriptor( Value )):
                builtins.print()
                continue
            
            builtins.print(f'(Value = {GetShortArgs(Value)})')
            
    
    Dump(Obj, Static = Static)
    
    ...
    
def ArgDecorator( Arg ):
    
    print("Arg = ", Arg)
    Pause()
    
    def ActualDecorator( TargetFunction ):
    
        @wraps( TargetFunction )
        def FunctionWrapper( *args, **kwargs):
            print("Hello")
            ReturnValue  =  TargetFunction( *args, **kwargs )
            return ReturnValue
        
        return FunctionWrapper
    

    return ActualDecorator
    

    
def CheckMemory( TargetFunction ):
    
    @wraps( TargetFunction )
    def FunctionWrapper( *args, **kwargs ):
        
        # first, run full GC to clear everything it can
        gc.collect()
        
        # start the tracemalloc with 25 traceback frame history
        tracemalloc.start( 25 )

        # clear all prior trace data and reset peak data
        tracemalloc.clear_traces()
        tracemalloc.reset_peak()
    
        # before calling target function, get the current 
        # traced memory info that should be a decently clean state
        
        # get_traced_memory() returns a tuple of 2 ints 
        # representing bytes. I wanted megabytes so divide them
        # by 1024*1000 and round to 2 digits.

        MB = 1024 * 1000
        
        #
        # one way to make megabytes, converting the tuple of ints
        # to a list and using map to divide and round:
        #
        # HeapSize, PeakSize = map( round, map( operator.truediv,
        #                      list( tracemalloc.get_traced_memory() ), 
        #                      [MB, MB]), [2, 2])
        #
        # another way, converting the tuple to a list comprehension
        # then back to a tuple:
        #
        # HeapSize, PeakSize = tuple(
        #     list( *( (round( x / MB, 2), round( y / MB, 2))
        #     for x, y in ( tracemalloc.get_traced_memory(), ))))
        #
        # or just doing the simple thing:
        
        HeapSize, PeakSize = tracemalloc.get_traced_memory()
        HeapSize = round( HeapSize / MB, 4)
        PeakSize = round( PeakSize / MB, 4)
        
        print()
        print("------------------------------------------------------")
        print( f"Before calling        : {TargetFunction.__name__}" )
        print( f"Current Heap Size MB  : {HeapSize}")
        print( f"Peak Heap Size MB     : {PeakSize}" )
        print("------------------------------------------------------")
        print()
        
        # take the "before" tracemalloc snapshot
        Snapshot1  =  tracemalloc.take_snapshot()
        
        # run GC again just before calling function
        gc.collect()
        
        # call target function
        ReturnValue  =  TargetFunction( *args, **kwargs )
        
        # run GC again just after function returns
        gc.collect()
        
        # take the "after" tracemalloc snapshot
        Snapshot2  =  tracemalloc.take_snapshot()
        
        HeapSize, PeakSize = tracemalloc.get_traced_memory()
        HeapSize = round( HeapSize / MB, 4)
        PeakSize = round( PeakSize / MB, 4)
        
        print()
        print("------------------------------------------------------")
        print( f"After calling         : {TargetFunction.__name__}" )
        print( f"Current Heap Size MB  : {HeapSize}")
        print( f"Peak Heap Size MB     : {PeakSize}" )
        
        # get diff stats from snapshots
        SnapshotDiff = Snapshot2.compare_to(
                                 Snapshot1, 
                                 key_type = 'lineno' )
        
        # stop tracemalloc
        tracemalloc.stop()
        
        print()
        print( "Top Heap Differences:" )
        print()
        
        TotalDiff = 0.0
        
        for Idx, Stat in enumerate( SnapshotDiff[:5], 1 ):
        
            Frame       = Stat.traceback[0]
            DiffSize    = round( Stat.size_diff / MB, 4 )
            File        = Frame.filename.split( os.sep )[-1]
            Line        = Frame.lineno
            Code        = linecache.getline( File, Line ).strip()
            TotalDiff   += Stat.size_diff  

            print(f"{Idx}: Size: {DiffSize} MB, " +
                  f"File: {File}, Line: {Line}, " + 
                  f"Code: \"{Code}\"")
    
        TotalDiff = round( TotalDiff / MB, 4 )
        
        print()
        print(f"Total: {TotalDiff} MB")
        print()
        print("------------------------------------------------------")
        print()
        return ReturnValue    
    return FunctionWrapper
    ...
    

colorama_init(autoreset=True)
    
if __name__ == '__main__':
    print("Hello, world")
    
'''
    for i in inspect.getmembers(Test1):
        
        # builtins.print(type(i[1]))
        
        builtins.print('member: ' + str(i[0]))
        obj = i[1]
        
        if (inspect.ismodule( obj )):
            builtins.print('ismodule')

        if (inspect.isclass( obj )):
            builtins.print('isclass')
            builtins.print(inspect.getmro(obj))
            builtins.print( str( inspect.getclasstree( [obj] ) ) )
            
        if (inspect.ismethod( obj )):
            builtins.print('ismethod')
            
            #builtins.print(inspect.formatargvalues(inspect.getfullargspec(obj)))
            #for x in inspect.getmembers( obj ):
            #    builtins.print(x)

        if (inspect.isfunction( obj )):
            builtins.print('isfunction')
            builtins.print(inspect.getfullargspec(obj))
            
        if (inspect.isgeneratorfunction( obj )):
            builtins.print('isgeneratorfunction')
        
        if (inspect.isgenerator( obj )):
            builtins.print('isgenerator')

        if (inspect.istraceback( obj )):
            builtins.print('istraceback')

        if (inspect.isframe( obj )):
            builtins.print('isframe')

        if (inspect.iscode( obj )):
            builtins.print('iscode')

        if (inspect.isbuiltin( obj )):
            builtins.print('isbuiltin')

        if (inspect.isroutine( obj )):
            builtins.print('isroutine')
            builtins.print(inspect.getfullargspec(obj))
'''



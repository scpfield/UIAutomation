import sys, io, time, random, json, copy, gc, linecache, inspect
from more_itertools import ncycles

import app_config
import apps
import app_pages
from util import *

import selenium.webdriver
import appium.webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.mouse_button import MouseButton
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.wheel_input import WheelInput
#from selenium.webdriver.remote.command import Command as RemoteCommand
from selenium.webdriver.remote.command import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import *
from selenium.common.exceptions import *
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.webelement import WebElement

AndroidAttributeNames = [
    'resource-id', 'name', 'text', 'original-text', 
    'class', 'package', 'displayed', 'checkable', 
    'checked', 'clickable', 'content-desc', 'enabled', 
    'focusable', 'focused', 'longClickable', 'password', 
    'scrollable', 'selection-start', 'selection-end', 
    'selected', 'hint', 'extras', 'bounds' ]

AndroidPropertyNames = [
    'id', 'location', 'size', 'accessible_name',
    'aria_role', 'tag_name', 'shadow_root' ]
  

class NoIterListsException(Exception):
    ...
  
class AppElement():

    def __init__( self, *args, **kwargs ):
            
        for Arg, ArgValue in kwargs.items():
            if Arg == 'Attributes' and ArgValue:
                for Key, Value in ArgValue.items():
                    #print("Setting Arg: " + Key)
                    setattr(self, Key, Value)
                    #FixedKey = str(Key.replace('-','_'))
                    #setattr(self, FixedKey, Value)
            else:
                setattr(self, Arg, ArgValue)
    
        #Info(self)
        self.IterLists = []
        self.InitializeW3CActions()
        ...
   
    def __copy__( self ):
            
        CopyObj      = type( self )(
          Name       = copy.copy(self.Name),
          Tag        = copy.copy(self.Tag),
          Text       = copy.copy(self.Text),
          Tail       = copy.copy(self.Tail),
          Attributes = copy.copy(self.Attributes),
          ObjPath    = copy.copy(self.ObjPath),
          XPath      = copy.copy(self.XPath),
          Selector   = copy.copy(self.Selector),
          Locator    = copy.copy(self.Locator),
          Instance   = None )
 
        if 'Parent' in self.__dict__:
            setattr( CopyObj, 'Parent', self.Parent )
            
        #if 'Parent' in self.__dict__:
        #    setattr( CopyObj, 'Parent', copy.copy( self.Parent ))
            
        for ChildObj in self:
            setattr( CopyObj, ChildObj.Name, ChildObj )
        
        return CopyObj
        ...


    # method for 
    def Ancestors( self, MaxHeight = None ):
       
        # sub-function for traversal of object tree
        # using this instance as the starting point
        # the reason is to flatten a tree into a list
        
        def TraverseNodes( CurrentNode = None, NodeList = None, Height = None ):
            
            if CurrentNode   == None: CurrentNode   = self
            if NodeList      == None: NodeList      = []
            if Height        == None: Height         = 0
            if Height > 0:   NodeList.append( CurrentNode )
            
            if hasattr(CurrentNode, 'Parent'):
                ParentNode = CurrentNode.Parent
                if ParentNode:
                    if ( MaxHeight != None ) and ( Height > MaxHeight ):
                        ...
                    else:
                        TraverseNodes(  ParentNode, NodeList, ( Height + 1) )

        # end of TraverseNodes sub-function
        
        # perform upward recursion to find parent nodes
        # of this node in the tree and add them to a list
        AncestorList = []
        TraverseNodes( self, AncestorList )
        
        # make a new dictionary with the data
        NewListEntry = {}
        NewListEntry['StackHash']   = hash(Stack(Print = False))
        NewListEntry['ListData']    = AncestorList
        NewListEntry['ListPtr']     = 0
        
        # add to the list of the lists
        # of lists that callers are iterating upon
        self.IterLists.append(NewListEntry)
        return self
        ...

    def Descendants( self, MaxDepth = None ):
       
        # sub-function for traversal of object tree
        # using this instance as the starting point
        # the reason is to flatten a tree into a list
        
        def TraverseNodes( CurrentNode = None, NodeList = None, Depth = None ):
            
            if CurrentNode   == None: CurrentNode   = self
            if NodeList      == None: NodeList      = []
            if Depth         == None: Depth         = 0
            if Depth > 0:    NodeList.append( CurrentNode )
            
            for Key in CurrentNode.__dict__:
                if isinstance( CurrentNode.__dict__[Key], AppElement ):
                    if Key != 'Parent':
                        if ( MaxDepth != None ) and ( Depth > MaxDepth ):
                            continue
                        ChildNode = CurrentNode.__dict__[Key]
                        TraverseNodes(  ChildNode, NodeList, ( Depth + 1) )

        # end of TraverseNodes sub-function
        
        # perform downward recursion to find child nodes
        # of this node in the tree and add them to a list
        DescendantList = []
        TraverseNodes( self, DescendantList )
            
        # make a new dictionary with the data
        NewListEntry = {}
        NewListEntry['StackHash']   = hash(Stack(Print = False))
        NewListEntry['ListData']    = DescendantList
        NewListEntry['ListPtr']     = 0

        # add to a book-keeping list of the lists
        # that callers are iterating upon
        self.IterLists.append(NewListEntry)
        return self
        ...

        
    def __call__(self, MyMethod):
        return MyMethod()
        
    #  __iter__ is called by python once at the beginning
    #  of a 'for / in' loop for any initialization.
    #  we don't have any, so just return ourself
    def __iter__(self):        
        if len( self.IterLists ) == 0:
            raise NoIterListsException
        return self    

    # __next__ is called by python for each iteration
    # of a 'for / in' loop
    # we don't remove items in any given data list
    # during an iteration of it, only at the end 
    # we remove the whole list from our list of lists
    def __next__(self):
        if len( self.IterLists ) > 0:
            ListEntry   = self.IterLists[ -1 ]
            ListPtr     = ListEntry.get( 'ListPtr' )
            ListData    = ListEntry.get( 'ListData' )
            if  ListPtr > ( len( ListData ) - 1 ):
                self.IterLists.pop()
                raise StopIteration
            else:
                Value = ListData[ ListPtr ]
                ListEntry[ 'ListPtr' ] += 1
                return Value
        else: raise StopIteration
        ...
        
    # __len__ is called by python when using len()
    # it returns the length of the current data list    
    def __len__( self ):
        if len( self.IterLists ) > 0:
            ListEntry   = self.IterLists[ -1 ]
            ListData    = ListEntry.get( 'ListData' )
            Value       = len( ListData )
            return Value
        else: return 0
        ...
      
    # __getitem__ is called by python when using 
    # bracket notation to access items in a list by
    # index, or dictionary by key, such as: object[5]
    # weird thing is if this is being called by list
    # comprehension it just keeps incrementing the index
    # until you raise StopIteration
    # also getitem is called when using the "reversed" iterator
    def __getitem__(self, Index):
    
        print("__getitem__: " + str(Index))
        if len( self.IterLists ) > 0:
            ListEntry   = self.IterLists[-1]
            ListData    = ListEntry.get( 'ListData' )
            if Index < ( len( ListData )):
                return ListData[Index]
            else: raise StopIteration
        else: return None
        ...
   
    # this is to implement "if / in" functionality
    def __contains__( self, Arg ):
    
        #print("__contains__: " + str(Arg))
        
        if not Arg: return False
        
        SearchDescendants   = False
        Depth               = 0
        Items               = None
        
        if  isinstance( Arg, tuple ):
            if  len( Arg ) < 2:
                Items = Arg[ 0 ]
            else:
                Items = Arg[ 0 ]
                if      Arg[ 1 ]:
                        SearchDescendants = True
                        Depth             = None
        else: Items = Arg
        
        if  not isinstance( Items, list ):
            Items = [ Items ]
        
        for Item in Items:
        
            # Search for Element objects
            if isinstance( Item, AppElement ):
                Result = ([   
                            Element.ObjPath
                            for Element in self.Descendants( Depth )
                            if  Element == Item 
                          ])
                
                #print(f"{len(Result)} exist in Node / Descendants")
                if     len( Result ) > 0: continue
                else:  return False            

            # Search for Attribute Names using strings
            if isinstance( Item, str ):
                Result = ([   
                            Element.ObjPath
                            for Element in self.Descendants()
                            if ((   not SearchDescendants       )   and
                                (   Item in self.__dict__       ))  
                                or
                                ((  SearchDescendants           )   and
                                ((  Item  in  self.__dict__     )   or
                                 (  Item  in  Element.__dict__  )))
                         ])
                
                # print(f"{len(Result)} exist in Node / Descendants")
                if     len( Result ) > 0: continue
                else:  return False

            # Search for Attributes Names + Values using Dictionary
            if isinstance( Item, dict ):
                
                SearchElements = [ self ]
                
                if SearchDescendants:
                    SearchElements.extend( self.Descendants() )
                    
                for Key, Value in Item.items():

                    Elements = ([   Element 
                                    for  Element in SearchElements
                                    if   Element.__dict__.get(Key) == Value
                                ])
                    
                    if    Elements: SearchElements = Elements
                    else: return False
                        
                    
                #print(f"{len(Elements)} element exists in Node / Descendants")
                
                if     len( Elements ) > 0: continue
                else:  return False
                
                
        return True
        ...
    

    def __lt__( self, Other ):
        
        return ( len(self.ObjPath.split('.')) < 
                 len(Other.ObjPath.split('.')))
        
    def __gt__( self, Other ):
        
        return ( len(self.ObjPath.split('.')) > 
                 len(Other.ObjPath.split('.')))

        
    def __repr__( self ):
        return str( self.__dict__ )
    
    def __bool__( self ):
        return True
        
    def __str__( self ):
        return str( self.__dict__)
    
    def __eq__( self, Other ):
    
        if isinstance( Other, AppElement ):
            if self.ObjPath == Other.ObjPath:
                return True
            else:
                return False
        else:
            return False
        ...
            
    def __hash__( self ):
        return hash( self.ObjPath )
        ...
        
    def InitializeW3CActions( self ):
        ...

    def CreateDriverInstance( self ):
        
        PollFrequencySec = 0.25
        Timeout = 2
        ConditionFunction = presence_of_element_located

        WaitFor = WebDriverWait(
                    driver = app_config.Driver,
                    timeout = Timeout,
                    poll_frequency = PollFrequencySec,
                    ignored_exceptions = [
                        NoSuchElementException,
                        StaleElementReferenceException ] )
        
        try:
            Instance = WaitFor.until(
                        ConditionFunction(
                            (self.Locator,
                            (self.Selector))))
                
            if ( ( isinstance(
                    Instance, 
                    selenium.webdriver.remote.webelement.WebElement )) or
                 ( isinstance(
                    Instance, 
                    appium.webdriver.webelement.WebElement ))):
                self.Instance = Instance
                return True
            else:
                return False

        except TimeoutException as te:
            print('Exceeded timeout while waiting')
            GetExceptionInfo(te)
            Pause()
            return False
            
        except BaseException as be:
            print('Exception')
            GetExceptionInfo(be)
            Pause()
            return False        
            
        ...

    def ClearW3CActions(self):
        for Device in self.InputActions.w3c_actions.devices:
            Device.clear_actions()
        ...

...  # end of AppElement class


class ScrollableElement():

    SCROLL_RESULT_SCROLLED  = 1
    SCROLL_RESULT_EOL       = 2
    SCROLL_RESULT_ERROR     = 3

    def __init__( self ):
        ...
    
    def ScrollToStart( self, Duration ):
        ...
    
    def ScrollToEnd( self, Duration ):
        ...
    
    def ScrollForward( self, Duration ):
        ...
    
    def ScrollBackward( self, Duration ):
        ...

    def VerifyScroll( self ):
        ...

class FocusableElement():

    def __init__( self ):
        ...
        
    def SetFocus( RepeatCount = 1, Duration = 50):
        ...
        
class EditableElement():

    def __init__( self ):
        ...
        
    def SendKeys( self, Text ):
    
        if not self.Instance:
            if not self.CreateDriverInstance():
                print("Failed to create Driver Instance")
                return False
            else:
                print("CREATED NEW INSTANCE")
        
        print("Driver Element ID: " + str(self.Instance.id))
        self.Instance.send_keys( Text )
        

    def SetValue( self, Value ):
    
        Result = None
        Script = ( f"return ({self.DOMPath}.value = '{Value}');" )
        
        try:
            print(Script)
            Result = app_config.Driver.execute( 
                        Command.W3C_EXECUTE_SCRIPT,
                        { 'script' : Script,
                          'args'   : []  } ) 

        except BaseException as e:
            GetExceptionInfo(e)
            Pause()
            return None
        
        if Result:  return Result.get('value')
        else:       return None


    def GetValue( self ):
    
        Result = None
        Script = ( f"return {self.DOMPath}.value;" )
        
        try:
            print(Script)
            Result = app_config.Driver.execute( 
                        Command.W3C_EXECUTE_SCRIPT,
                        { 'script' : Script,
                          'args'   : []  } ) 

        except BaseException as e:
            GetExceptionInfo(e)
            Pause()
            return None
        
        if Result:  return Result.get('value')
        else:       return None
    
        
class ClickableElement():

    def __init__( self, *args, **kwargs ):
        print("CLICKABLE_ELEMENT CONSTRUCTOR") 
        ...
        
    def Click( self, RepeatCount = 1, Duration = 50 ):
    
        if not self.Instance:
            if not self.CreateDriverInstance():
                print("Failed to create Driver Instance")
                return False
            else:
                print("CREATED NEW INSTANCE")
        
        print("Button ID: " + str(self.Instance.id))
        self.Instance.click()



class MobileElement( AppElement ):

    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
    ...
        
    def InitializeW3CActions( self ):
    
        self.KeyInputSource             =   KeyInput( 
                                                interaction.KEY )
        self.WheelInputSource           =   WheelInput(
                                                interaction.WHEEL)                                                
        self.TouchInputSource           =   PointerInput(
                                                interaction.POINTER_TOUCH, 
                                                RandomString(10) )
        self.PenInputSource             =   PointerInput(
                                                interaction.POINTER_PEN, 
                                                RandomString(10) )                                                
        self.MouseInputSource           =   PointerInput(
                                                interaction.POINTER_MOUSE, 
                                                RandomString(10) )                                            
                                                
        self.PointerInputSource         =   self.MouseInputSource
        self.InputActions               =   ActionChains( app_config.Driver )
        self.InputActions.w3c_actions   =   ActionBuilder(
                                              app_config.Driver,
                                              keyboard = self.KeyInputSource,
                                              wheel    = self.WheelInputSource,
                                              mouse    = self.PointerInputSource )

        self.PointerAction              = self.InputActions.w3c_actions.pointer_action
        self.KeyAction                  = self.InputActions.w3c_actions.key_action
        self.WheelAction                = self.InputActions.w3c_actions.wheel_action

        self.ClearW3CActions()
        
        return True
        ...

...  # end of MobileElement class


class ScrollableAndroidElement( ScrollableElement ):
    
    def __init__( self ):
    
        super().__init__()


    def Initialize( self, IndexParentElement = None, ScrollingChildIDs = None ):

        print("Initializing ScrollableAndroidElement with:")
        print("IndexParentElement: " + IndexParentElement.Name)
        print("ScrollingChildIDs: " + str(ScrollingChildIDs))
        
        self.AssociatedElements                     = app_config.Container()
        self.AssociatedElements.IndexParentElement  = IndexParentElement
        self.AssociatedElements.ScrollingChildIDs   = ScrollingChildIDs
        
        print(self.AssociatedElements.IndexParentElement.Name)
        print(str(self.AssociatedElements.ScrollingChildIDs))
        
        ...


    def ScrollToStart( self, Duration = 250 ):
        
        print('Called')

        while True:

            Result = self.ScrollBackward( Duration )
            
            match Result:
                case ScrollableElement.SCROLL_RESULT_SCROLLED:
                    print('SCROLL_RESULT_SCROLLED')
                case ScrollableElement.SCROLL_RESULT_EOL:
                    print('SCROLL_RESULT_EOL')
                    return True
                case ScrollableElement.SCROLL_RESULT_ERROR:
                    print('SCROLL_RESULT_ERROR')
                    return False
        ...

    def ScrollToEnd( self, Duration = 250 ):
        
        print('Called')
        
        while True:
            
            Result = self.ScrollForward( Duration )           
            
            match Result:
                case ScrollableElement.SCROLL_RESULT_SCROLLED:
                    print('SCROLL_RESULT_SCROLLED')
                case ScrollableElement.SCROLL_RESULT_EOL:
                    print('SCROLL_RESULT_EOL')
                    return True
                case ScrollableElement.SCROLL_RESULT_ERROR:
                    print('SCROLL_RESULT_ERROR')
                    return False
        ...


    def ScrollForward( self, Duration = 250 ):
        
        print('Called') 
        
        StartX   = self.bounds.get('CenterX')
        StartY   = self.bounds.get('Y2')
        EndX     = self.bounds.get('CenterX')
        EndY     = self.bounds.get('Y1') * 0.90
        Result   = None
        # print(f'{StartX}, {StartY}, {EndX}, {EndY}')
        
        try:
        
            self.PointerAction.move_to_location(
                 x = StartX, 
                 y = StartY, 
                 duration = Duration )
            self.PointerAction.pointer_down(
                 duration = 0 )
            self.PointerAction.move_to_location( 
                 x = EndX, 
                 y = EndY, 
                 duration = Duration )
            self.PointerAction.pointer_up()
            self.PointerAction.pause()
            self.InputActions.perform()
            
            return self.VerifyScroll()
                
        except Exception as e:
            GetExceptionInfo(e)
            return False
            
        return True
        ...


    def ScrollBackward( self, Duration = 250 ):
    
        print('Called') 
        
        StartX   = self.bounds.get('CenterX')
        StartY   = self.bounds.get('Y1')
        EndX     = self.bounds.get('CenterX')
        EndY     = self.bounds.get('Y2') * 0.90
        Result   = None
        # print(f'{StartX}, {StartY}, {EndX}, {EndY}')
        
        try:
        
            self.PointerAction.move_to_location(
                 x = StartX, 
                 y = StartY, 
                 duration = Duration )
            self.PointerAction.pointer_down(
                 duration = 0 )
            self.PointerAction.move_to_location( 
                 x = EndX, 
                 y = EndY, 
                 duration = Duration )
            self.PointerAction.pointer_up()
            self.PointerAction.pause()
            self.InputActions.perform()
            
            return self.VerifyScroll()
                
        except Exception as e:
            GetExceptionInfo(e)
            return False
            
        return True
        ...

    def VerifyScroll(self):
    
        # Current page tree and ScrollIndexParentElement
        CurrentElementTree       = app_config.CurrentPage.PageElementTree
        CurrentScrollIndexParent = self.AssociatedElements.IndexParentElement
        
        # Get a new ElementTree from server
        NewElementTree           = app_pages.AndroidAppPage.CreateElementTree()
        
        # Find matching scroll elements in new element tree
        # The test for equality is custom using __eq___
        NewScrollableElement     = [ Element 
                                     for Element in NewElementTree.Descendants()
                                     if  Element == self ][0]
        
        NewIndexParentElement    = [ Element 
                                     for Element in NewElementTree.Descendants() 
                                     if  Element == CurrentScrollIndexParent ][0]
                                      
        
        if not NewScrollableElement:
            print('Unable to locate NewScrollableElement in NewElementTree')
            return ScrollableElement.SCROLL_RESULT_ERROR
        
        if not NewIndexParentElement:
            print('Unable to locate NewIndexParentElement in NewElementTree')
            return ScrollableElement.SCROLL_RESULT_ERROR
        
        
        print('GETTING CURRENT INDEX ELEMENTS')

        AllCurrentScrollIndexElements   = set( list(
                                        Element
                                        for Element in CurrentScrollIndexParent.Descendants(0)
                                        if  Element.Parent == CurrentScrollIndexParent ))
                                             
        AllCurrentScrollIndexValues     = set( list(
                                        Element.index
                                        for Element in AllCurrentScrollIndexElements ))
                                        
        CurrentVisibleScrollIndexValues = set( list(
                                          Element.index
                                          for Element in AllCurrentScrollIndexElements
                                          if  Element.displayed == True ))

        print('GETTING NEW INDEX ELEMENTS')
       
        AllNewScrollingIndexElements    = set( list(
                                          Element
                                          for Element in NewIndexParentElement.Descendants(0)
                                          if Element.Parent == NewIndexParentElement ))
        
        AllNewScrollingIndexValues      = set( list(
                                          Element.index
                                          for Element in AllNewScrollingIndexElements ))
        
        SymmetricDifference             = set( 
                                          CurrentVisibleScrollIndexValues ^ 
                                          AllNewScrollingIndexValues )
        
        print("All Current Scrolling    : " + str( AllCurrentScrollIndexValues ))
        print("Current Visible          : " + str( CurrentVisibleScrollIndexValues ))
        print("All New Scrolling        : " + str( AllNewScrollingIndexValues ))
        print("Difference               : " + str( SymmetricDifference ))
        print('Difference Length        : ' + str(len( SymmetricDifference )))
        
        if len( SymmetricDifference ) > 0:
            Result = ScrollableElement.SCROLL_RESULT_SCROLLED
        else:
            Result = ScrollableElement.SCROLL_RESULT_EOL
            
        # update element tree
        # first, set all scrolling index elements to non-visible
        for Element in AllCurrentScrollIndexElements:
            #print('Resetting current scrolling element to non-visible: ' + Element.Name)
            setattr( Element, 'displayed', False )
        
        # replace current elements with new elements
        for Element in AllNewScrollingIndexElements:
            #print('Replacing current scrolling element with new: ' + Element.Name)
            setattr( Element, 'Parent', CurrentScrollIndexParent)
            setattr( CurrentScrollIndexParent, Element.Name, Element )
 
        return Result
        ...

    def GetScrollingElementIndexValues( self, IndexParentElement = None ):
        
        if IndexParentElement  ==  None:
            IndexParentElement  =  self.AssociatedElements.IndexParentElement
                                      
        return sorted( list(
                       Element.index 
                       for Element in IndexParentElement.Descendants(0)
                       if  Element.Parent == IndexParentElement ))
                       #if not self.IsPartialScrollingElement( Element ) ))
    
        
    def FindAllScrollingIndexElements( self, Duration = 250 ):
    
        Total = 0

        # First, scroll to start of list
        
        if not self.ScrollToStart( Duration = Duration ):
            print("Failed to ScrollToStart")
            return ScrollableElement.SCROLL_RESULT_ERROR

        ScrollingIndexElements = self.GetScrollingElements()
        
        if not ScrollingIndexElements:
            print("Failed to GetScrollingElements")
            return ScrollableElement.SCROLL_RESULT_ERROR
        
        print(f'Total Scrolling Elements = ' + 
              f'{len(ScrollingIndexElements)}')
        
        # now scroll in stages, checking for new scroll child elements
        ScrollFunctionList = [ self.ScrollForward, 
                               self.ScrollBackward ]
        Result  = False
        Gap     = False
        
        for ScrollFunction in ncycles( ScrollFunctionList, 10 ):
    
            while True:

                Result = ScrollFunction( Duration = Duration )

                match Result:
                    case ScrollableElement.SCROLL_RESULT_SCROLLED:
                        print('SCROLL_RESULT_SCROLLED')
                    case ScrollableElement.SCROLL_RESULT_EOL:
                        print('SCROLL_RESULT_EOL')
                        break
                    case ScrollableElement.SCROLL_RESULT_ERROR:
                        print('SCROLL_RESULT_ERROR')
                        return False
                
                ScrollingIndexElements = self.GetScrollingElements()
                
                if not ScrollingIndexElements:
                    print("Failed to GetScrollingElements")
                    return ScrollableElement.SCROLL_RESULT_ERROR
                    
                print(f'Total Scrolling Elements = ' + 
                      f'{len(ScrollingIndexElements)}')
            ...        

            ScrollingIndexElements = self.GetScrollingElements()

            if not ScrollingIndexElements:
                print("Failed to GetScrollingElements")
                return ScrollableElement.SCROLL_RESULT_ERROR
                                     
            print(f'Total Scrolling Elements = ' + 
                  f'{len(ScrollingIndexElements)}')

            # get sorted list of all scroll elements found
            
            SortedIndexValues = self.GetScrollingElementIndexValues()
            
            if not SortedIndexValues:
                print("Failed to GetScrollingElements")
                return ScrollableElement.SCROLL_RESULT_ERROR
            
            # check for gaps
            # sometimes the list can start with 1 instead of 0
            # first check is for start gaps
            
            #if SortedIndexValues[0] > 1:
            #    Gap = True
            #else:
            
            # Use set dynamic difference to show other gaps
            FullRangeSet = set(range(SortedIndexValues[0],
                                     SortedIndexValues[-1] + 1))
            
            DynamicDifference = set( set(SortedIndexValues) ^ FullRangeSet )
            
            if len(DynamicDifference) > 0:
            
                Gap = True
                print('Gaps detected in Scrolling Index Elements:')
                print(str(DynamicDifference))
                
            else:
                Result = True
                print('No gaps found')
                break
                
            print("Switching directions to fill gaps")
            
        return Result
        ...
        
    
    def IsPartialScrollingElement( self, ScrollingIndexElement = None,
                                         IndexParentElement    = None ):
        
        if not IndexParentElement:
               IndexParentElement = self.AssociatedElements.IndexParentElement
        
        ChildResourceIDs          = self.AssociatedElements.ScrollingChildIDs
        
        FoundChildElements        = [ ( Element, ResourceID )
                                      for Element in ScrollingIndexElement.Descendants()
                                      for ResourceID in ChildResourceIDs
                                      if  ResourceID in Element.resource_id ]

        if len( FoundChildElements ) < len( ChildResourceIDs ):
            print("FOUND PARTIAL: ", ScrollingIndexElement.Name)
            
        return len( FoundChildElements ) < len( ChildResourceIDs )
            
        
    def GetScrollingElementByIndex( self, ScrollingElementIndex ):
        
        print("GetScrollingElementByIndex called")
        IndexParentElement = self.AssociatedElements.IndexParentElement
        
        return [ Element
                 for Element in self.AssociatedElements.IndexParentElement.Descendants(0)
                 if  Element.Parent == IndexParentElement
                 if  Element.index  == ScrollingElementIndex ][0]
        
    
    def GetScrollingElements( self, IndexParentElement = None ):
        
        if not IndexParentElement:
               IndexParentElement = self.AssociatedElements.IndexParentElement
        
        return [ Element 
                 for Element in IndexParentElement.Descendants(0)
                 if  Element.Parent == IndexParentElement ]
    
    def IsVisibleScrollingIndexElement( self, TargetElementIdx ):
        
        ScrollingIndexElements  = [ Element.index
                                    for Element in self.AssociatedElements.IndexParentElement.Descendants(0)
                                    if  Element.Parent == self.AssociatedElements.IndexParentElement ]
                           
        VisibleIndexValues      = sorted( list(
                                  Element.index 
                                  for Element in self.AssociatedElements.IndexParentElement.Descendants(0)
                                  if  Element.Parent == self.AssociatedElements.IndexParentElement
                                  if  Element.displayed == True ))

        FirstVisibleIdx         = VisibleIndexValues[0]
        LastVisibleIdx          = VisibleIndexValues[-1]
        Result                  = None

        if TargetElementIdx < FirstVisibleIdx:
            Distance    = TargetElementIdx - FirstVisibleIdx
            Result      = ( False, Distance )
            
        elif TargetElementIdx > LastVisibleIdx:
            Distance    = TargetElementIdx - LastVisibleIdx
            Result      = ( False, Distance )
            
        else:
            Distance    = 0
            #Distance    = int(( FirstVisibleIdx - LastVisibleIdx ) / 2 )
            Result      = ( True, Distance )
            
        
        print( f'FirstVisibleIdx   = {FirstVisibleIdx}'  )
        print( f'LastVisibleIdx    = {LastVisibleIdx}'   )
        print( f'TargetElementIdx  = {TargetElementIdx}' ) 
        print( f'Distance          = {Distance}'         )    
        
        if FirstVisibleIdx >= LastVisibleIdx:
            print()
            print( f'IsVisible ERROR: Indexes out of order' )
            Pause()
        
        return Result
    ...    

    def ScrollIntoViewByIndex( self, 
                        TargetElementIdx,
                        Duration = 250):

        print()
        print('--------------------------------------------------')
        print( f"ScrollIntoView called for: " + 
               f"{TargetElementIdx}" )
        
        Visible = False
        Partial = False
        ScrollFunction = None
        Result = None
        
        while not Visible:
            
            Visible, Distance = self.IsVisibleScrollingIndexElement( 
                                     TargetElementIdx )
            
            # break if element is visible and not partial
            if Visible: return True
            
            # choose scroll direction to find the element
            if Distance > 0:
                ScrollFunction = self.ScrollForward
                
            if Distance < 0:
                ScrollFunction = self.ScrollBackward
            
            # execute a scroll
            Result = ScrollFunction( Duration = Duration )
            
            match Result:
                case ScrollableElement.SCROLL_RESULT_SCROLLED:
                    print('SCROLL_RESULT_SCROLLED')
                case ScrollableElement.SCROLL_RESULT_EOL:
                    print('SCROLL_RESULT_EOL')
                case ScrollableElement.SCROLL_RESULT_ERROR:
                    print('SCROLL_RESULT_ERROR')
                    return False
                    
            # loop back again
        ...
        

class ClickableAndroidElement( ClickableElement ):

    def __init__( self ):
        ...

    def Click( self, RepeatCount = 1, Duration = 50 ):
        self.Tap( RepeatCount = RepeatCount, 
                  Duration = Duration)
                  
    def Tap( self, RepeatCount = 1, Duration = 50 ):
        
        print("Called")
        
        CenterX  = self.Attributes.get('bounds').get('CenterX')
        CenterY  = self.Attributes.get('bounds').get('CenterY')

        try:
        
            for x in range( RepeatCount ):
                
                self.PointerAction.move_to_location( 
                    x = CenterX, 
                    y = CenterY, 
                    duration = Duration )
                
                self.PointerAction.pointer_down( 
                    duration = Duration )
                    
                self.PointerAction.pointer_up()
                
                self.InputActions.perform()
                    
        except BaseException as e:
            GetExceptionInfo(e)
            #Pause()
            return False
            
        return True
    ...        
        
    
        
class FocusableAndroidElement( FocusableElement ):

    def __init__( self ):
        super().__init__()
        
    def SetFocus(self, RepeatCount = 1, Duration = 50):

        CenterX  = self.Attributes.get('bounds').get('CenterX')
        CenterY  = self.Attributes.get('bounds').get('CenterY')

        try:
        
            for x in range( RepeatCount ):
                
                self.PointerAction.move_to_location( 
                    x = CenterX, 
                    y = CenterY, 
                    duration = Duration )
                
                self.PointerAction.pointer_down( 
                    duration = Duration )
                
                self.InputActions.perform()
                    
        except BaseException as e:
            GetExceptionInfo(e)
            return False
            
        return True
    ...
    
class AndroidElement( MobileElement ):

    LOCATOR_ANDROID = '-android uiautomator'

    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
    ...

    @classmethod
    def NewElement( cls, *args, **kwargs ):

        BaseClassSet    = set()
        ElementAttrs    = kwargs.get('Attributes')
        
        match ElementAttrs:
            case { 'scrollable' : True }:
                BaseClassSet.add( ScrollableAndroidElement )
            case { 'focusable' :  True }:
                BaseClassSet.add( FocusableAndroidElement )
            case { 'clickable' :  True }:
                BaseClassSet.add( ClickableAndroidElement )

        BaseClassTuple = ( AndroidElement, )
        
        for Item in BaseClassSet:
            BaseClassTuple += ( Item, )
            
        #print(f"Creating new: {BaseClassTuple}" )
        
        return ( type( 'AndroidElement', 
                        BaseClassTuple, 
                        {} )
                        ( *args, **kwargs ) )    

    
    def Swipe( self, 
               StartX = None, StartY= None, 
               EndX = None, EndY = None, 
               Duration = 250):
        print("Hello")
        
...   # end of AndroidElement class


class WebAppElement( AppElement ):

    LOCATOR_CSS     = 'css selector'

    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        ...

    @classmethod
    def NewElement( cls, *args, **kwargs ):
      
        BaseClassSet    = set()
        ElementTag      = kwargs.get('Tag')
        ElementAttrs    = kwargs.get('Attributes')
        
        match ElementTag:
            case 'button' | 'input':
                BaseClassSet.add( ClickableElement )
                BaseClassSet.add( FocusableElement )
            case 'textarea':
                BaseClassSet.add( EditableElement )
                BaseClassSet.add( FocusableElement )
                

        match ElementAttrs:
            case { 'role' : ( 'button' | 'checkbox' ) }:
                BaseClassSet.add( ClickableElement )
                BaseClassSet.add( FocusableElement )
            case { 'type' : ( 'text' | 'password' ) }:
                BaseClassSet.add( EditableElement )
                BaseClassSet.add( FocusableElement )
            case { 'class' : Value } if Value and 'button' in Value:
                BaseClassSet.add( ClickableElement )
                BaseClassSet.add( FocusableElement )
            case { 'href' : Value } if Value:
                BaseClassSet.add( ClickableElement )
                BaseClassSet.add( FocusableElement )
            case { 'data-hash' : Value } if Value:
                BaseClassSet.add( ClickableElement )
                BaseClassSet.add( FocusableElement )
            case { 'data-component-type' : Value } if Value:
                BaseClassSet.add( ClickableElement )
                BaseClassSet.add( FocusableElement )                
            
            
        BaseClassTuple = ( WebAppElement, )
        
        for Item in BaseClassSet:
            BaseClassTuple += ( Item, )
            
        #print(f"Creating new: {BaseClassTuple}" )
        
        return ( type( 'WebAppElement', 
                        BaseClassTuple, 
                        {} )
                        ( *args, **kwargs ) )

    def InitializeW3CActions( self ):
    
        # print('InitializingW3CActions')
        
        self.KeyInputSource             =   KeyInput( 
                                                interaction.KEY )
        self.WheelInputSource           =   WheelInput(
                                                interaction.WHEEL )
        self.MouseInputSource           =   PointerInput(
                                                interaction.POINTER_MOUSE, 
                                                interaction.POINTER_MOUSE )
        self.PointerInputSource         =   self.MouseInputSource
        self.InputActions               =   ActionChains( app_config.Driver )
        self.InputActions.w3c_actions   =   ActionBuilder(
                                                app_config.Driver,
                                                keyboard    = self.KeyInputSource,
                                                wheel       = self.WheelInputSource,
                                                mouse       = self.PointerInputSource )
                                                
        self.PointerAction              = self.InputActions.w3c_actions.pointer_action
        self.KeyAction                  = self.InputActions.w3c_actions.key_action
        self.WheelAction                = self.InputActions.w3c_actions.wheel_action

        self.ClearW3CActions()
        
        return True
        ...


    def GetInnerHTML( self ):
    
        Result = None
        Script = ( f"return {self.DOMPath}." +
                   f"innerHTML;" )
        
        try:
        
            Result = app_config.Driver.execute( 
                        Command.W3C_EXECUTE_SCRIPT,
                        { 'script' : Script,
                          'args'   : []  })
                          
        except BaseException as e:
            #GetExceptionInfo(e)
            #Pause()
            return False
        
        if Result:  return Result.get('value')
        else:       return False
            
            
    def SetInnerHTML( self, Text = None ):
    
        Result = None
        Script = ( f'return ({self.DOMPath}.' +
                   f'innerHTML = "{Text}");' )
        
        try:
        
            print(Script)
            
            Result = app_config.Driver.execute( 
                        Command.W3C_EXECUTE_SCRIPT,
                        { 'script' : Script,
                          'args'   : []  })
                          
        except BaseException as e:
            GetExceptionInfo(e)
            Pause()
            return False
        
        if Result:  return Result.get('value')
        else:       return False


    def GetOuterHTML( self ):
    
        Result = None
        Script = ( f"return {self.DOMPath}." +
                   f"outerHTML;" )
        
        try:
        
            Result = app_config.Driver.execute( 
                        Command.W3C_EXECUTE_SCRIPT,
                        { 'script' : Script,
                          'args'   : []  })
                          
        except BaseException as e:
            GetExceptionInfo(e)
            Pause()
            return False
        
        if Result:  return Result.get('value')
        else:       return False            

    def GetAttributes( self ):
    
        Result = None
        Script = f"return {self.DOMPath}.attributes"
        
        try:
        
            Result = app_config.Driver.execute( 
                        Command.W3C_EXECUTE_SCRIPT,
                        { 'script' : Script,
                          'args'   : []  } ) 

        except BaseException as e:
            #Pause("GetAttributes Exception:")
            #GetExceptionInfo(e)
            return None
        
        if Result:  return Result.get('value')
        else:       return None
    
    def GetNodeName( self ):
    
        Result = None
        Script = ( f"return {self.DOMPath}.nodeName;" )
        
        try:
            print(Script)
            Result = app_config.Driver.execute( 
                        Command.W3C_EXECUTE_SCRIPT,
                        { 'script' : Script,
                          'args'   : []  } ) 

        except BaseException as e:
            GetExceptionInfo(e)
            Pause()
            return None
        
        if Result:  return Result.get('value')
        else:       return None    
    
    def GetNodeValue( self ):
    
        Result = None
        Script = ( f"return {self.DOMPath}.nodeValue;" )
        
        try:
            print(Script)
            Result = app_config.Driver.execute( 
                        Command.W3C_EXECUTE_SCRIPT,
                        { 'script' : Script,
                          'args'   : []  } ) 

        except BaseException as e:
            GetExceptionInfo(e)
            Pause()
            return None
        
        if Result:  return Result.get('value')
        else:       return None
        
        
    def GetNodeType( self ):
    
        Result = None
        Script = ( f"return {self.DOMPath}.nodeType;" )
        
        try:
            print(Script)
            Result = app_config.Driver.execute( 
                        Command.W3C_EXECUTE_SCRIPT,
                        { 'script' : Script,
                          'args'   : []  } ) 

        except BaseException as e:
            GetExceptionInfo(e)
            Pause()
            return None
        
        if Result:  return Result.get('value')
        else:       return None

        
    def GetAttribute( self, Name ):
    
        Result = None
        Script = ( f"return {self.DOMPath}." +
                   f"getAttribute('{Name}');" )
        
        try:
        
            Result = app_config.Driver.execute( 
                        Command.W3C_EXECUTE_SCRIPT,
                        { 'script' : Script,
                          'args'   : []  } ) 

        except BaseException as e:
            #GetExceptionInfo(e)
            #Pause()
            return None
        
        if Result:  return Result.get('value')
        else:       return None
            
    
    def RemoveAttribute( self, Name ):
    
        Result = None
        Script = ( f"return {self.DOMPath}." +
                   f"removeAttribute('{Name}');" )
        
        CurrentValue = self.GetAttribute(Name)
        
        if not CurrentValue:
            print('Attribute does not exist, no need to remove')
            return True
        else:
            try:
            
                Result = app_config.Driver.execute( 
                            Command.W3C_EXECUTE_SCRIPT,
                            { 'script' : Script,
                              'args'   : []  } ) 

            except BaseException as e:
                GetExceptionInfo(e)
                Pause()
                return False
        
        if Result:
            
            print("old value: " + str(CurrentValue))
            print("new value: " + str(self.GetAttribute(Name)))
            
            if CurrentValue == self.GetAttribute(Name):
                return False
            else:
                return True
        
        return False
        
    def SetAttribute( self, Name, Value ):

        CurrentValue    = None
        NewValue        = None
        Result          = None
        
        CurrentValue    = self.GetAttribute( Name )
        
        if CurrentValue == None:
            ...
            #print('Failed to get Attribute')
            
        if CurrentValue:
            
            if not self.RemoveAttribute( Name ):
            
                print('Failed to remove existing Attribute: ' + 
                        str(CurrentValue))
                        
                return None
            
        Script = ( f"return {self.DOMPath}." +
                   f"setAttribute('{Name}','{Value}');" )
                   
        try:
        
            Result =  app_config.Driver.execute( 
                        Command.W3C_EXECUTE_SCRIPT,
                        { 'script' : Script,
                          'args'   : []  } ) 

        except BaseException as e:
            #GetExceptionInfo(e)
            #Pause()
            return None
        
        if Result:  
            NewValue = Result.get('value')
            setattr(self, Name, Value)
            return NewValue
        else:
            return None

        
        
    def Hide( self ):
                
        Result        = None
        NewStyle      = None
        HideStyle     = "display:none"
        CurrentStyle  = self.GetAttribute('style')
        
        if not CurrentStyle:
            NewStyle = HideStyle
        else:
            CurrentStyle = CurrentStyle.strip()
            CurrentStyle += f" {HideStyle}"

        return self.SetAttribute('style', HideStyle)
                

    def Show( self ):
    
        Result        = None
        HideStyle     = "display:none"
        NewStyle      = None
        CurrentStyle  = self.GetAttribute('style')
        
        if not CurrentStyle:
            return True
        else:
            if HideStyle in CurrentStyle:
                NewStyle = ( 
                    CurrentStyle.replace(HideStyle, '').strip() )
                    
                return self.SetAttribute('style', NewStyle)
            else:
                return False


# Custom JSON Serializer stand-alone function            
def JSONSerializer(Obj):
        
    if isinstance( Obj, AppElement ):
       
        # make an object copy
        ObjCopy = copy.copy(Obj)
        ObjDict = ObjCopy.__dict__
        
        # to prevent circular loops, remove children of parent

        Parent = ObjDict.get('Parent')
        if Parent:
        
            ParentChildDeleteItems = []
            for Key, Value in Parent.__dict__.items():
                
                #print(Key, type(Value))
                
                if Key == 'Parent':
                    continue
                
                if not isinstance( Value, AppElement ):
                    continue
                
                #print('Appending to ParentChildDeleteItems: ' + Key)
                ParentChildDeleteItems.append(Key)

            for Item in ParentChildDeleteItems:
                #print('Deleting parent key: ' + Item)
                del Parent.__dict__[Item]


        KeepItems = [ 'Name', 'Tag', 'Text', 'Tail',
                      'Attributes', 'ObjPath', 'XPath',
                      'Selector', 'Locator' ]
                      
              
        DeleteItems = []
        
        for Key, Value in ObjDict.items():
        
            #print(Key, type(Value))
            
            if Key in KeepItems:
                continue
                
            if isinstance( Value, AppElement ):
                continue
                
            #print('Appending to self DeleteItems: ' + Key)
            DeleteItems.append(Key)
                
        for Item in DeleteItems:
            #print('Deleting self key: ' + Item)
            del ObjDict[Item]
        
        return(ObjDict)
    
...



if __name__ == '__main__':
    print('Hello, world')



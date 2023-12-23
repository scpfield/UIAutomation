import sys, io, time, random, json, copy
from abc import *

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
from selenium.webdriver.remote.command import Command as RemoteCommand
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import *
from selenium.common.exceptions import *
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.webelement import WebElement

import app_elements
from util import *

class MobileScrollFunctions( ABC ):

    def __init__( self ):
        ...
    
    @abstractmethod
    def ScrollToStart( this ):
        ...
        
    @abstractmethod
    def ScrollToEnd( this ):
        ...

    @abstractmethod
    def ScrollForward( this ):
        ...
        
    @abstractmethod
    def ScrollBackward( this ):
        ...

    @abstractmethod
    def FlingToStart( this ):
        ...
        
    @abstractmethod
    def FlingToEnd( this ):
        ...

    @abstractmethod
    def FlingForward( this ):
        ...
        
    @abstractmethod
    def FlingBackward( this ):
        ...
...


class AndroidScrollFunctions( MobileScrollFunctions ):

    def __init__( self ):
        super().__init__()



        

    @staticmethod
    def FlingToStart( ScrollableElement ):
        return ScrollToStart( ScrollableElement )
        
    @staticmethod
    def FlingToEnd( ScrollableElement ):
        return ScrollToEnd( ScrollableElement )

    @staticmethod
    def FlingForward( ScrollableElement ):
        return ScrollForward( ScrollableElement )
        
    @staticmethod
    def FlingBackward( ScrollableElement ):
        return ScrollBackward( ScrollableElement )

    @staticmethod
    def FindPartialScrollElement( Container = None, Node = None ):
        
        Result = None
        
        if Container == None: return False
        if Node      == None: Node = Container
        
        HasIcon     = False
        HasTitle    = False
        HasSummary  = False
        
        if (( Node.IsDescendantOf( Container )) and
            ( Node.Name == 'RecyclerView_0' )):
                
                for LastChild in Node:
                    ...

                if LastChild.IsParentOf( 'LinearLayout_0' ):
                    if LastChild.LinearLayout_0.IsParentOf( 'ImageView_0' ):
                        HasIcon = True
                    
                if LastChild.IsParentOf( 'RelativeLayout_1' ):
                    
                    if LastChild.RelativeLayout_1.IsParentOf( 'TextView_0' ):
                        HasTitle = True
                
                    if LastChild.RelativeLayout_1.IsParentOf( 'TextView_1' ):
                        HasSummary = True
        
                if not HasIcon or not HasTitle or not HasSummary:
                    print('LastChild item is missing child nodes:')
                    print(f"{LastChild.ObjPath}")
                    print(f'{HasIcon}, {HasTitle}, {HasSummary}')
                    return LastChild
                else:
                    print('LastChild is not missing any child nodes')
                    return False
        
        for ChildNode in Node:
            Result = AndroidScrollFunctions.FindPartialScrollElement(
                Container, ChildNode)
        
        return Result
        
    
    @staticmethod
    def ScrollForwardByIncrement( Container = None, App=None, IncrementPct = 1.0, VerifyScroll = True):
    
        print('ScrollForwardByIncrement: called')
        
        # RootElement = App.RootElement
        
        StartX   = Container.Attributes['bounds']['CenterX']
        StartY   = Container.Attributes['bounds']['Y2'] # + 1
        EndX     = Container.Attributes['bounds']['CenterX']
        EndY     = Container.Attributes['bounds']['Y1'] # - 1
        Duration = 350
        Result   = None
        FailCount = 0
        
        while True:
            # get the full max height of the visible elements via
            # parent object lookup which has the real height, using
            # fancy list incomprehension feature
            SortedHeights = sorted( 
                [ ParentObj.Parent.Parent.Attributes['bounds']['Height'] 
                  for ParentObj in Container.GetVisibleScrollElements() ] )
            
            print(str(SortedHeights))
            MinHeight = SortedHeights[0]
            MaxHeight = SortedHeights[-1]
            Distance = int( ((MaxHeight - MinHeight) + MaxHeight) * IncrementPct)
            Duration = 250
            print()
            print(f'IncrementPct = {IncrementPct}')
            print(f'ScrollByIncrement: {StartX}, {StartY}, {EndX}, {EndY}')
            print(f'MaxHeight = {MaxHeight}, MinHeight = {MinHeight}, Distance = {Distance}')
            print(f'StartY-Distance = {StartY-Distance}')
        
            try:
                Container.PointerAction.move_to_location( x = StartX, y = StartY, duration = 100 )
                Container.PointerAction.pointer_down(duration=50)
                Container.PointerAction.move_to_location( x = StartX, y = StartY - Distance, duration = 150 )
                Container.PointerAction.release()
                Container.InputActions.perform()
        
                ScrollResult = None
                if VerifyScroll:
                
                    ScrollResult = Container.VerifyScrollFunction()

                    if isinstance( ScrollResult, app_elements.AppElement ):
                        Container = ScrollResult
                    else:
                        print('Incrementing fail count for verifyscroll')
                        FailCount += 1
                        if FailCount > 5:
                            return ScrollResult
                else:
                    Container = App.RefreshData()
                    return Container
                    
                # check for missing elements
                # print(f"{Container.Name}, {Container.ObjPath}")
                FindPartialResult = AndroidScrollFunctions.FindPartialScrollElement( 
                                    Container )
                
                if FindPartialResult:
                    print('Last element has missing tags')
                    FailCount2 = 0
                    while True:
                         
                        print('Attempting tiny scroll')
                        ScrollResult = AndroidScrollFunctions.ScrollForwardByIncrement(
                                        Container = Container, App = App, IncrementPct = 0.5, 
                                        VerifyScroll = False)
                        
                        Container = ScrollResult
                        
                        FindPartialResult = AndroidScrollFunctions.FindPartialScrollElement( 
                                            Container )
                        
                        if not FindPartialResult:
                            break
                        
                        FailCount2 += 1
                        if FailCount2 > 20:
                            print('Tried 5 times to tiny scroll, exiting')
                            return False

                #return ScrollResult
                
            except ( StaleElementReferenceException, 
                     NoSuchElementException,
                     BaseException) as e:
                GetExceptionInfo(e)
                Pause()
                return False
      
        ...
        
    ...  


class UiAutomatorScrollFunctions( MobileScrollFunctions ):

    def __init__(self):
        super().__init__()

    @staticmethod
    def ScrollToStart( this, MaxSpeed       = 10, 
                             MaxSwipes      = 50, 
                             VerifyFunction = None):
    
        print('ScrollToStart: Called')

        FunctionSelector = ''
        Args = ''
        
        if not MaxSpeed:
            Args = str( MaxSwipes )
        else:
            Args = str( MaxSwipes ) + ',' + str( MaxSpeed )
        ...
        
        FunctionSelector = str( this.Selector + 
                                '.scrollToBeginning(' + 
                                Args + 
                                ')' )
        
        Result = this.ExecuteScroll( FunctionSelector )
        
        if not Result: return False
        
        if VerifyFunction:
            return VerifyFunction()
        else:
            return True
        ...    
    ...    
        
    @staticmethod    
    def ScrollToEnd(this, MaxSpeed       = 10, 
                          MaxSwipes      = 50, 
                          VerifyFunction = None ):

        print('ScrollToEnd: Called')

        FunctionSelector = ''
        Args = ''
        
        if not MaxSpeed:
            Args = str( MaxSwipes )
        else:
            Args = str( MaxSwipes ) + ',' + str( MaxSpeed )
        ...
        
        FunctionSelector = str( this.Selector + 
                                '.scrollToEnd(' + 
                                Args + 
                                ')' )
        
        Result = this.ExecuteScroll( FunctionSelector )
        
        if not Result: return False
        
        if VerifyFunction:
            return VerifyFunction()
        else:
            return True
        ...    
    ...    

    @staticmethod
    def ScrollForward(this, MaxSpeed       = 10, 
                            MaxSwipes      = 50, 
                            VerifyFunction = None ):
                        
        print('ScrollForward: Called')

        FunctionSelector = ''
        Args = ''
        
        if not MaxSpeed:
            Args = ''
        else:
            Args = str( MaxSpeed )
        ...
        
        FunctionSelector = str( this.Selector + 
                                '.scrollForward(' + 
                                Args + 
                                ')' )
        
        Result = this.ExecuteScroll( FunctionSelector )
        
        if not Result: return False
        
        if VerifyFunction:
            return VerifyFunction()
        else:
            return True
        ...    
    ...   

    @staticmethod
    def ScrollBackward(this, MaxSpeed       = 10, 
                             MaxSwipes      = 50, 
                             VerifyFunction = None ):
                        
                        
        print('ScrollBackward: Called')

        FunctionSelector = ''
        Args = ''
        
        if not MaxSpeed:
            Args = ''
        else:
            Args = str( MaxSpeed )
        ...
        
        FunctionSelector = str( this.Selector + 
                                '.scrollBackward(' + 
                                Args + 
                                ')' )
        
        Result = this.ExecuteScroll( FunctionSelector )
        
        if not Result: return False
        
        if VerifyFunction:
            return VerifyFunction()
        else:
            return True
        ...    
    ...   

    @staticmethod
    def FlingToStart(this, MaxSpeed       = 10, 
                           MaxSwipes      = 50, 
                           VerifyFunction = None ):
                        
        print('FlingToStart: Called')
        
        FunctionSelector = ''
        Args = str( MaxSwipes )
        
        FunctionSelector = str( this.Selector + 
                                '.flingToBeginning(' 
                                + Args + 
                                ')' )
        
        Result = this.ExecuteScroll( FunctionSelector )
        
        if not Result: return False
        
        if VerifyFunction:
            return VerifyFunction()
        else:
            return True
        ...    
    ...   
        
    @staticmethod
    def FlingToEnd(this, MaxSpeed       = 10, 
                         MaxSwipes      = 50, 
                         VerifyFunction = None ):
                        
        print('FlingToEnd: Called')

        FunctionSelector = ''
        Args = str( MaxSwipes )
        
        FunctionSelector = str( this.Selector + 
                                '.flingToEnd(' + 
                                Args + 
                                ')' )
        
        Result = this.ExecuteScroll( FunctionSelector )
        
        if not Result: return False
        
        if VerifyFunction:
            return VerifyFunction()
        else:
            return True
        ...    
    ...   
        
    @staticmethod
    def FlingForward(this, MaxSpeed       = 10, 
                           MaxSwipes      = 50, 
                           VerifyFunction = None ):
                        
        print('FlingForward: Called')
        
        FunctionSelector = ''
        Args = ''
        
        FunctionSelector = str( this.Selector + 
                                '.flingForward(' + 
                                Args + 
                                ')' )
        
        Result = this.ExecuteScroll( FunctionSelector )
        
        if not Result: return False
        
        if VerifyFunction:
            return VerifyFunction()
        else:
            return True
        ...    
    ...     
    
    @staticmethod
    def FlingBackward(this, MaxSpeed       = 10, 
                            MaxSwipes      = 50, 
                            VerifyFunction = None ):
                        
        print('FlingBackward: Called')

        FunctionSelector = ''
        Args = ''
        
        FunctionSelector = str( this.Selector + 
                                '.flingBackward(' + 
                                Args + 
                                ')' )
        
        Result = this.ExecuteScroll( FunctionSelector )
        
        if not Result: return False
        
        if VerifyFunction:
            return VerifyFunction()
        else:
            return True
        ...    
    ... 

    @staticmethod
    def ExecuteScroll(this, FunctionSelector):
        
        if not this.Instance:
            if not this.CreateWebDriverInstance():
                print('ExecuteScroll: Failed to create instance for: ' + this.Name)
                return False
            else:
                print('ExecuteScroll: Created new instance for: ' + this.Name)
        ...
        
        PollFrequencySec = 0.25
        Timeout = 2
        ConditionFunction = presence_of_element_located

        WaitFor = WebDriverWait(
                    driver = this.Driver,
                    timeout = Timeout,
                    poll_frequency = PollFrequencySec,
                    ignored_exceptions = [
                        NoSuchElementException,
                        StaleElementReferenceException ] )
        
        try:
        
            Instance = WaitFor.until(
                             ConditionFunction(
                                ( this.Locator,
                                ( FunctionSelector ))))
                
            if ( (isinstance(Instance, selenium.webdriver.remote.webelement.WebElement)) or
                 (isinstance(Instance, appium.webdriver.webelement.WebElement)) ):
                this.Instance = Instance
                return True
            else:
                return False
            ...
            
        except TimeoutException as te:
            print('CreateWebDriverInstance: Exceeded timeout while waiting')
            Stack()
            Pause()
            return False
        except BaseException as be:
            print('CreateWebDriverInstance: Exception')
            Stack()
            Pause()
            return False     
        ...
    ...    
...  # end of UiAutomatorScrollFunctions class


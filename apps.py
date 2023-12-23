import sys, io, time, random, json, xml.etree.ElementTree as ET, lxml.html, lxml.etree
from copy import copy
from more_itertools import ncycles

from selenium import webdriver
from selenium.webdriver.remote.command import *
import appium.webdriver

import app_config
import app_pages
import app_elements
from util import *



class DriverInitException(Exception):
    ...
    
class TestApp():
    
    def __init__( self, UseAppium = True ):
        if not self.InitializeDriver( UseAppium ):
            raise DriverInitException
        
        app_config.App  = self
        
        self.CurrentPageName = ''
        app_config.CurrentPageName = self.CurrentPageName
        
        ...
    
    def ExitApp( self ):
        if app_config.Driver:
            print('Closing app_config.Driver')
            app_config.Driver.quit()
            app_config.Driver = None
            return True
        else: 
            print('No app_config.Driver to close')
            return False
        ...

    def LoadPage( self, PageName = None, Target = None, WaitFor = None ):
        
        try:
            
            if Target:
                
                if isinstance(self, WebApp):
                    app_config.Driver.get( Target )
                
                if isinstance(self, AndroidApp):
                    app_config.Driver.start_activity( self.Package, self.Activity )
            
            
            DriverName   = self.WaitForPage( WaitFor = WaitFor )            
            
            if not DriverName:
                print('Failed to wait for the page')
                return False
            
            Page = self.NewPage( App = self, PageName = PageName )

            if not Page:
                print('Failed to create page')
                return False
            
            
            setattr( self, PageName, Page)
            
            self.CurrentPageName        = PageName
            self.CurrentPage            = Page
            
            app_config.CurrentPageName  = self.CurrentPageName
            app_config.CurrentPage      = self.CurrentPage
            
            return True
            
        except BaseException as e:
            GetExceptionInfo(e)
            return False
        
        
    def WaitForPage( self, WaitFor = None):
        
        DriverPageName  = None
        MaxCount        = 10
        Count           = 0
                
        # wait for app activity/page to change
        while Count < MaxCount:

            Count += 1
            DriverPageName = self.GetDriverPageName()
            
            print("DriverPageName  : "  + DriverPageName)
            print("CurrentPageName : "  + self.CurrentPageName)
            
            if DriverPageName == self.CurrentPageName:
                print(f"Waiting for DriverPageName to change. " +
                      f"Count = {Count}")
                time.sleep( 0.5 )
                
            else:
                print('DriverPageName has changed to: ' + DriverPageName)
                break
        
        if Count == MaxCount:
            print('DriverPageName did not change after waiting')
            return None
        
        # if caller did not ask to wait for anything else we're done
        if not WaitFor:
            return DriverPageName
        
        # even if the activity/page has changed, it may not be
        # fully loaded and ready, so if the caller specifies a
        # resource-id of an element to wait for, then wait for it
        
        MaxCount    = 10
        Count       = 0
        
        while Count < MaxCount:
            
            Result = None
            Count += 1
                    
            # search to find an element that exists 
            if ( WaitFor, True ) in self.GetElementTree():
            
                print( f"Found: {WaitFor}" )
                return DriverPageName
            
            else:
                print( f"Waiting for: {WaitFor}, Count = {Count}" )
                time.sleep(0.5)
        
        if Count == MaxCount:
            print(f"Could not find: {WaitFor}" )
            return None
        ...

    def NewPage( self, *args, **kwargs ):
                            
        print('Creating new Page')
        
        # intercept args and adjust if needed
        App         = kwargs['App']
        PageName    = kwargs['PageName']
        UniqueName  = None
        
        # check if the requested page already exists
        if hasattr(App, PageName):
        
            print("Page name collision")
            
            # append random string to requested page name
            UniqueName = PageName + '_' + RandomString(5)
            
            kwargs['PageName'] = UniqueName
            print('Renamed page to: ' + UniqueName)
            
        Page = None
        Page = self.LoadPageType()( *args, **kwargs )
        return Page
        ...
        
    def InitializeDriver( self, UseAppium ):
        ...
        
    def GetDriverPageName( self ):
        ...
        
... # end of TestApp base class
    
    
class WebApp( TestApp ):

    def __init__( self, UseAppium = True ):
        print('Called')
        super().__init__( UseAppium )
        ...
    
    def LoadPageType( self ):
        return app_pages.WebAppPage
        
    def InitializeDriver(self, UseAppium = True ):
        
        try:
            if not UseAppium:
                print('Initializing Selenium app_config.Driver')
                
                CapabilityParameters = {}
                Capabilities = {}
                CapabilityParameters['acceptInsecureCerts'] = True
                CapabilityParameters['unhandledPromptBehavior'] = 'accept'
                CapabilityParameters['pageLoadStrategy'] = 'normal'
                Capabilities['capabilities'] = CapabilityParameters
                Capabilities['capabilities']['alwaysMatch'] = CapabilityParameters
                Capabilities['acceptInsecureCerts'] = True
                Capabilities['unhandledPromptBehavior'] = 'accept'                
                Capabilities['pageLoadStrategy'] = 'normal'
                
                MyOptions = webdriver.ChromeOptions()
                MyOptions.add_argument("high-dpi-support=1")
                MyOptions.add_argument("force-device-scale-factor=1.25")
                MyOptions.add_argument("allow-insecure-localhost")
                MyOptions.add_argument("allow-external-pages")
                MyOptions.add_argument("ignore-urlfetcher-cert-requests")
                MyOptions.add_argument("dark-mode-settings=1")
                
                #driver = webdriver.Chrome(options=options)
                app_config.Driver = webdriver.Chrome(
                                    desired_capabilities=Capabilities, 
                                    chrome_options=MyOptions)
                
            else:
                print('Initializing Appium app_config.Driver' )
                AppiumServer = 'http://127.0.0.1:4723'
                Capabilities = {}
                Capabilities['platformName']                    = 'Windows'
                Capabilities['appium:automationName']           = 'chromium'
                Capabilities['appium:newCommandTimeout']        = 2000
                app_config.Driver = appium.webdriver.Remote( AppiumServer, Capabilities )
                
        except BaseException as e:
            GetExceptionInfo(e)
            return None

        if app_config.Driver:
            app_config.Driver.set_page_load_timeout( 5000 )
            app_config.Driver.set_script_timeout( 5000 )
            app_config.Driver.implicitly_wait( 0 )
            print( 'app_config.Driver Initialization Complete' )
        
        return app_config.Driver != None
        ...

    def GetDriverPageName( self ):
         return str(app_config.Driver.current_url)
         
    def GetElementTree( self ):
        return app_pages.WebAppPage.CreateElementTree()
        

            
    
        
...  # end of WebApp class


class AndroidApp( TestApp ):

    def __init__( self ):
        super().__init__( UseAppium = True )

    def LoadPageType( self ):
        return app_pages.AndroidAppPage
        
    def InitializeDriver( self, UseAppium = True ):

        print('Initializing Appium app_config.Driver')
        
        try:
            Capabilities = {}
            Settings     = {}
            AppiumServer = 'http://127.0.0.1:4723'
            
            Capabilities['platformName']                = 'Android'
            Capabilities['appium:platformVersion']      = '13'
            Capabilities['appium:deviceName']           = 'emulator-5554'
            Capabilities['appium:automationName']       = 'uiautomator2'
            Capabilities['appium:nativeWebScreenshot']  = True
            Capabilities['appium:newCommandTimeout']    = 2000
            # Capabilities['appium:waitForIdleTimeout']       = 500
            # Capabilities['appium:waitForSelectorTimeout']   = 500
            # Capabilities['appium:scrollAcknowledgmentTimeout'] = 500
            # Capabilities['appium:actionAcknowledgmentTimeout']  = 500
            app_config.Driver = appium.webdriver.Remote( AppiumServer, Capabilities )
            
        except BaseException as e:
            GetExceptionInfo(e)
            return None

        if app_config.Driver:
            app_config.Driver.update_settings(Settings)
            app_config.Driver.implicitly_wait( 0 )
        
        return app_config.Driver != None
        ...    
    
    def GetDriverPageName( self ):
         return str(app_config.Driver.current_activity)
     
    def GetElementTree( self ):
        return app_pages.AndroidAppPage.CreateElementTree()
     


class AndroidSettingsApp( AndroidApp ):

    def __init__( self ):
        super().__init__()
        self.SettingsAppPackage  = 'com.android.settings'
        self.SettingsAppActivity = 'com.android.settings.Settings'
    ...
    
    def ScrollToAllElementsTest( self,
                             ScrollElement,
                             RandomSelection = False, 
                             Reverse         = False,
                             Duration        = 250 ):

        if ScrollElement == None:
            return False
            
        ScrollingElements = ScrollElement.GetScrollingElements()

        ScrollingElementsIndexValues = [ Element.index
                                         for Element in ScrollingElements ]
                           
        SortedIndexValues            = sorted( ScrollingElementsIndexValues )
                                    
        SelectionList                = None
        
        if RandomSelection:
            SelectionList            = random.sample( 
                                        SortedIndexValues, 
                                        len( SortedIndexValues ))
        else:
            if Reverse:
                SelectionList        = reversed( SortedIndexValues )
            else:
                SelectionList        = SortedIndexValues
                                
        
        for SelectedIdx in SelectionList:
        
            SelectedElement = ScrollElement.GetScrollingElementByIndex(SelectedIdx)
            
            print('Selected Element: ' + 
                  SelectedElement.Name + ", Idx = " + str(SelectedIdx))
                            
            if not getattr(SelectedElement, 'displayed'):
            
                Result = ScrollElement.ScrollIntoViewByIndex( 
                         SelectedIdx, Duration = Duration)
            
                if not Result:
                    print('Error scrolling element into view')
                    return False
            #else:
            #    print('Selected Element is already visible')

            SelectedElement = ScrollElement.GetScrollingElementByIndex(SelectedIdx)
    
            if ScrollElement.IsPartialScrollingIndexElement( SelectedElement ):
                print("SELECTED ELEMENT IS A PARTIAL!")
                Pause()
            #else:
            #    print("Selected Element is not a partial")

            Focusable = SelectedElement.Attributes.get('focusable')
            if Focusable:
                if not SelectedElement.SetFocus( RepeatCount = 1, Duration = 50 ):
                    print('Error setting element focus')
                    Pause()
                    return False
            else:
                print("Selected item is not a focusable item")
            
                        
        return True
        
    ...    

    def TestSetup(self):
    
        ScrollElementKey     = 'ScrollElement'
        PageWaitForKey       = 'PageWaitFor'
        IndexParentPathKey   = 'IndexParentPath'
        ScrollingChildsKey   = 'ScrollingChildIDs'
        
        Pages = {}
        
        Pages[0] = {}
        Pages[0][ScrollElement]      = StartPage.Scrollable.ScrollView_1_0
        Pages[0][PageWaitForKey]     = 'com.android.settings:id/container_material'
        Pages[0][IndexParentPathKey] = 'LinearLayout_0.FrameLayout_1.LinearLayout_0.FrameLayout_0.RecyclerView_0'
        Pages[0][ScrollingChildIDs]  = ['android:id/icon', 'android:id/title', 'android:id/summary']

        Pages[1] = {}
        Pages[1][ScrollableElement]  = Page.Scrollable.RecyclerView_0_0
        Pages[1][PageWaitForKey]     = 'com.android.settings:id/container_material'
        Pages[1][IndexParentPathKey] = ''
        Pages[1][ScrollingChildIDs]  = ['android:id/title']

        Pages[2] = {}
        Pages[2][PageWaitForKey]     = 'com.android.settings:id/container_material'
        Pages[2][IndexParentPathKey] = 'LinearLayout_0.FrameLayout_1.LinearLayout_0.FrameLayout_0.RecyclerView_0'
        Pages[2][ScrollingChildIDs]  = ['android:id/icon', 'android:id/title', 'android:id/summary']

        Pages[3] = {}
        Pages[3][PageWaitForKey]     = 'com.android.settings:id/container_material'
        Pages[3][IndexParentPathKey] = 'LinearLayout_0.FrameLayout_1.LinearLayout_0.FrameLayout_0.RecyclerView_0'
        Pages[3][ScrollingChildIDs]  = ['android:id/icon', 'android:id/title', 'android:id/summary']


    
    def GuessScrollIndexParentElement( self, Page ):
    
        PageTreeRoot         = Page.PageElementTree
        
        ScrollViewElement    = None
        RecyclerViewElement  = None
        
        ScrollViewElement    = [ Element
                                 for Element in PageTreeRoot.Descendants()
                                 if Element.scrollable  == True
                                 if Element.focusable   == True 
                                 if 'ScrollView' in Element.Name
                                 if 'id/main_content_scrollable_container' in Element.resource_id ][0]
                            
        RecyclerViewElement = [ Element
                                for Element in ScrollViewElement.Descendants()
                                if Element.scrollable == False
                                if Element.focusable  == True
                                if 'RecyclerView' in Element.Name
                                if 'id/recycler_view' in Element.resource_id ][0]
        

        if  ScrollViewElement and RecyclerViewElement:
            return ScrollViewElement, RecyclerViewElement

        #  if not the above, then it might be this
        
        ScrollViewElement    = [ Element
                                 for Element in PageTreeRoot.Descendants()
                                 #if Element.scrollable  == True
                                 #if Element.focusable   == False 
                                 if 'ScrollView' in Element.Name
                                 if 'id/main_content_scrollable_container' in Element.resource_id ][0]
                            
        RecyclerViewElement = [ Element
                                for Element in ScrollViewElement.Descendants()
                                if Element.scrollable == True
                                if Element.focusable  == True
                                if 'RecyclerView' in Element.Name
                                if 'id/recycler_view' in Element.resource_id ][0]
        
        if  ScrollViewElement and RecyclerViewElement:
            return ScrollViewElement, RecyclerViewElement
            
        
    # @CheckMemory
    def Test(self):

        print("AndroidSettingsApp Test")
        
        StartPage = self.StartApp( self.SettingsAppPackage, 
                                   self.SettingsAppActivity )
        
        if not StartPage:
            print('Failed to start app')
            self.ExitApp()
            return False
        
        StartPageRootNode = StartPage.PageElementTree
        
        # MyListIterator = iter(MyList)
        # print(len(MyListIterator))
        # TypeError: object of type 'list_iterator' has no len()
        # if "abc" in MyListIterator: print("iterator: yes") 
        # else: print("iterator: no")
        # if "abc" in MyListIterator: print("iterator: yes") 
        # else: print("iterator: no")
        # if "abc" in MyList: print("list: yes")
        # else: print("list: no")
        # if "abc" in MyList: print("list: yes")
        # else: print("list: no")

                
        # Additional initializations for the StartPage
        # primary scroll container element
        StartPageScrollViewElement, StartPageRecyclerViewElement = (
            self.GuessScrollIndexParentElement( StartPage ))
        
        StartPageScrollingChildIDs = [ 'android:id/icon',
                                       'android:id/title', 
                                       'android:id/summary' ]
        
        print(StartPageRecyclerViewElement.Name)
        print(StartPageScrollViewElement.Name)
        
        StartPageScrollViewElement.Initialize( 
                                   StartPageRecyclerViewElement,
                                   StartPageScrollingChildIDs )
        
        
        ObjectTreeRoot = app_config.CurrentPage.PageElementTree
                
        AllNodes = ([   Element
                        for  Element  in  ObjectTreeRoot.Descendants() 
                    ])
        
        
        print('AllNodes Count: ', len( AllNodes ))
        Pause()
    

        ClickableNodes = ([
        
                            Element
                    
                            for  Element  in  ObjectTreeRoot.Descendants() 
                    
                            if   Element.clickable  ==  True
                    
                         ])


        print('ClickableNodes Count: ', len( ClickableNodes ))
        Pause()

    
        AllLeafNodeNamesAndPaths = (

                [( 
                
                    Element.Name, Element.ObjPath    ,)
              
                    for  Element  in  AllNodes
                    
                    if   len( Element.Descendants() ) == 0
                    
                ])


        print('AllLeafNodeNamesAndPaths Count: ', 
          len( AllLeafNodeNamesAndPaths ))
        
        Pause()

        
        AllAncestorsOfNodesHavingTextData = (
        
                [(
                
                    Parent.Name,    Child.text       ,)
              
                    for  Parent       in     AllNodes
                    for  Child        in     AllNodes
              
                    #if   Parent       in     Child.Ancestors() 
                    #if   Child.text   and    len( Child.text ) > 0
                  
                ])

        
        print('AllAncestorsOfNodesHavingTextData Count: ', 
          len( AllAncestorsOfNodesHavingTextData ))
        Pause()    
        
        
        DescendentsOfDescendants = (
        
                [(
                
                    GrandParent,  Parent,  Child     ,)
              
                    for   GrandParent    in    AllNodes
                    for   Parent         in    GrandParent.Descendants()
                    for   Child          in    Parent.Descendants()
 
                    #if   Parent          in    Child.Ancestors()
                    #if   GrandParent     in    Parent.Ancestors()
                ])


        print('DescendentsOfDescendants Count: ', 
          len( DescendentsOfDescendants ))
        
        Pause()
        
        

        
        

        # Discover all of the scrolling elements by scrolling through
        # the list and finding the non-visible items to include in the
        # page element tree
        
        
        Result = StartPageScrollViewElement.FindAllScrollingIndexElements(
                                            Duration = 350)
     
        match Result:
            case app_elements.ScrollableElement.SCROLL_RESULT_SCROLLED:
                print('SCROLL_RESULT_SCROLLED')
            case app_elements.ScrollableElement.SCROLL_RESULT_EOL:
                print('SCROLL_RESULT_EOL')
            case app_elements.ScrollableElement.SCROLL_RESULT_ERROR:
                print('Failed to FindAllScrollingIndexElements')
                print('SCROLL_RESULT_ERROR')
                self.ExitApp()
                return False
        
        '''
        for x in range(1):
            if not self.ScrollToAllElementsTest( 
                                     StartPageScrollable,
                                     Duration = 250,
                                     Reverse = True,
                                     RandomSelection = False):
                                     
                print('Failed to ScrollToAllElementsText')
                self.ExitApp()
                return False

            if not self.ScrollToAllElementsTest( 
                             StartPageScrollable,
                             Duration = 250,
                             Reverse = False,
                             RandomSelection = False):
                             
                print('Failed to ScrollToAllElementsText')
                self.ExitApp()
                return False
        '''
        
        StartPage.EnumerateElementTree()
        
        
        #StartPageSubPages = StartPageScrollable.GetScrollingElementIndexValues()
        
        self.ExitApp()
        return True
        
        for SubPageIndex in StartPageSubPages:
            
            
            #StartPage.EnumerateElementTree()
            #StartPage.PageSourceToFile()
            #StartPage.ElementTreeToFile()
        
            Pause()
            print("About to enter sub-page: " + str(SubPageIndex))
            Pause()
            
            if not StartPageScrollable.ScrollIntoViewByIndex( 
                                       SubPageIndex ):
                                                
                print('Failed to scroll into view: ' + str(SubPageIndex))
                self.ExitApp()
                return False
            
            ScrollingElement = StartPageScrollable.GetScrollingElementByIndex( 
                                                   SubPageIndex )
        
            if not ScrollingElement:
                print('Failed to get scrolling element')
                self.ExitApp()
                return False
                           
            # Tap on the scrolling element to load the sub-page
            if not ScrollingElement.Tap( Duration = 50 ):
                print('Failed to tap element')
                self.ExitApp()
                return False
        
            # A new page should load as a result of the Tap
            # wait for it to be ready
            NewPageActivity = self.WaitForPage(
                              "android:id/navigationBarBackground")

            if not NewPageActivity:
                print('Failed to wait for new page activity to start')
                self.ExitApp()
                return False
            
            print('New Page/Activity: ' + NewPageActivity)
        
            NewPage = AndroidApp.NewPage( App = self,
                                          Name = NewPageActivity )
                                
            if not NewPage:
                print('Failed to create new page: ' + NewPageActivity)
                self.ExitApp()
                return False
                
            #NewPage.PageSourceToFile()
            #NewPage.ElementTreeToFile()
        
            NewPageIndexParent, NewPageScrollable = self.GetScrollElementPair( NewPage )

            if not NewPageIndexParent or not NewPageScrollable:
                print('Could not locate IndexParentElement/PageScrollable pair')
                self.ExitApp()
                return False
            
            Pause()
            
            NewPageScrollable.Initialize( IndexParentElement = NewPageIndexParent,
                                          ScrollingChildIDs  = [ 'android:id/title' ] )
                    
            
            if not NewPageScrollable.FindAllScrollingIndexElements():
                print('Failed to FindAllScrollingIndexElements')
                self.ExitApp()
                return False
            
            Pause()
            
            if not self.ScrollToAllElementsTest( 
                             NewPageScrollable,
                             Duration = 250,
                             Reverse = True,
                             RandomSelection = False):
                             
                print('Failed to ScrollToAllElementsText')
                self.ExitApp()
                return False

            if not self.ScrollToAllElementsTest( 
                             NewPageScrollable,
                             Duration = 250,
                             Reverse = False,
                             RandomSelection = False):
                             
                print('Failed to ScrollToAllElementsText')
                self.ExitApp()
                return False
        
            app_config.Driver.back()
            
        self.ExitApp()
        return True
    
...     # end of AndroidSettingsApp



if __name__ == '__main__':

    print('Hello, world')
    SettingsAppPackage  = 'com.android.settings'
    SettingsAppActivity = 'com.android.settings.Settings'
    
    
    #MyTestApp = AndroidSettingsApp() 
    #MyTestApp.Test()


'''
[AndroidUiautomator2app_config.Driver@21de]   waitForIdleTimeout
[AndroidUiautomator2app_config.Driver@21de]   waitForSelectorTimeout
[AndroidUiautomator2app_config.Driver@21de]   scrollAcknowledgmentTimeout
[AndroidUiautomator2app_config.Driver@21de]   actionAcknowledgmentTimeout
[AndroidUiautomator2app_config.Driver@21de]   locationContextEnabled
[AndroidUiautomator2app_config.Driver@21de]   autoAcceptAlerts
[AndroidUiautomator2app_config.Driver@21de]   javascriptEnabled
[AndroidUiautomator2app_config.Driver@21de]   pageJavascriptEnabled
[AndroidUiautomator2app_config.Driver@21de]   handlesAlerts
[AndroidUiautomator2app_config.Driver@21de]   mobileEmulationEnabled
[AndroidUiautomator2app_config.Driver@21de]   cssSelectorsEnabled
[AndroidUiautomator2app_config.Driver@21de]   rotatable
[AndroidUiautomator2app_config.Driver@21de]   nativeEvents
[AndroidUiautomator2app_config.Driver@21de]   allowInvisibleElements
[AndroidUiautomator2app_config.Driver@21de]   ignoreUnimportantViews
[AndroidUiautomator2app_config.Driver@21de]   enableMultiWindows
[AndroidUiautomator2app_config.Driver@21de]   disableIdLocatorAutocompletion
[AndroidUiautomator2app_config.Driver@21de]   shouldUseCompactResponses
[AndroidUiautomator2app_config.Driver@21de]   trackScrollEvents
[AndroidUiautomator2app_config.Driver@21de]   disableAndroidWatchers
'''

'''
        #Capabilities['appium:browserName']         = 'Chrome'
        Capabilities['appium:waitForIdleTimeout']                   = 500
        Capabilities['appium:waitForSelectorTimeout']               = 500
        Capabilities['appium:scrollAcknowledgmentTimeout']          = 500
        Capabilities['appium:actionAcknowledgmentTimeout']          = 500
        Capabilities['appium:locationContextEnabled']               = True
        Capabilities['appium:autoGrantPermissions']                 = True
        Capabilities['appium:autoAcceptAlerts']                     = True
        Capabilities['appium:javascriptEnabled']                    = True
        Capabilities['appium:pageJavascriptEnabled']                = True
        Capabilities['appium:handlesAlerts']                        = True
        Capabilities['appium:mobileEmulationEnabled']               = False
        Capabilities['appium:cssSelectorsEnabled']                  = True
        Capabilities['appium:rotatable']                            = True
        Capabilities['appium:nativeEvents']                         = False
        Capabilities['appium:allowInvisibleElements']               = False
        Capabilities['appium:ignoreUnimportantViews']               = False
        Capabilities['appium:enableMultiWindows']                   = True
        Capabilities['appium:disableIdLocatorAutocompletion']       = True
        Capabilities['appium:shouldUseCompactResponses']            = False
        Capabilities['appium:unicodeKeyboard']                      = False
        Capabilities['appium:resetKeyboard']                        = False
        Capabilities['appium:trackScrollEvents']                    = True
        Capabilities['appium:disableAndroidWatchers']               = False
        Capabilities['appium:disableWindowAnimation']               = False
        Capabilities['appium:ignoreHiddenApiPolicyError']           = True
        Capabilities['appium:disableSuppressAccessibilityService']  = False
        Capabilities['appium:ensureWebviewsHavePages']              = False
        
        Settings['locationContextEnabled']                  = True
        Settings['disableWindowAnimation']                  = False
        Settings['disableAndroidWatchers']                  = False
        Settings['allowInvisibleElements']                  = False
        Settings['ignoreUnimportantViews']                  = False
        Settings['enableMultiWindows']                      = True
        Settings['disableIdLocatorAutocompletion']          = True
        Settings['shouldUseCompactResponses']               = False
        Settings['newCommandTimeout']                       = 1000
        Settings['waitForIdleTimeout']                      = 500
        Settings['waitForSelectorTimeout']                  = 500
        Settings['scrollAcknowledgmentTimeout']             = 500
        Settings['actionAcknowledgmentTimeout']             = 500
        Settings['disableSuppressAccessibilityService']     = True
        Settings['ignoreHiddenApiPolicyError']              = True
        Settings['trackScrollEvents']                       = True
        Settings['javascriptEnabled']                       = True
        Settings['pageJavascriptEnabled']                   = True
        Settings['handlesAlerts']                           = True
        Settings['mobileEmulationEnabled']                  = True
        Settings['cssSelectorsEnabled']                     = True
        Settings['rotatable']                               = True
        Settings['nativeEvents']                            = True
        Settings['autoAcceptAlerts']                        = True
   
        # Capabilities['appium:noSign'] = True
        # Capabilities['appium:appPackage']  =  'com.android.settings'
        # Capabilities['appium:appActivity'] =  'com.android.settings.Settings'
'''


'''
    def GetSubAppTitleElement(self, Title):
        
        def FindSubAppTitleElement(ElementObject = None, Title = Title):
            
            if ElementObject == None:
                ElementObject = self.SubAppRootNode
            
            if Title == 'Tips & support':
                if ElementObject.Selector == 'new UiSelector().resourceId("com.google.android.gms:id/gh_help_toolbar_text").className("android.view.ViewGroup").description("Help").index(1)':
                    print('FindSubAppTitleElement: Found SubAppTitleElement = ' + str(Title))
                    return ElementObject
            
            if 'class' in ElementObject.Attributes and 'content-desc' in ElementObject.Attributes:
                if ((ElementObject.Attributes['class'] == 'android.widget.FrameLayout') and
                    (ElementObject.Attributes['content-desc'] == str(Title))):
                        print('FindSubAppTitleElement: Found SubAppTitleElement = ' + str(Title))
                        return ElementObject
            
            for ChildObject in ElementObject:
                ElementResult = FindSubAppTitleElement(ChildObject, Title)
                if ElementResult != None:
                    return(ElementResult)
            return(None)
        
        while True:
            
            RootNode = self.CreateElementTree()
            # self.ElementTreeToFile(RootNode)
 
            SubAppTitleElement = FindSubAppTitleElement(
                                 ElementObject = RootNode, 
                                 Title = Title)
                                    
            if SubAppTitleElement != None:
                
                self.SubAppRootNode = RootNode
                
                if SubAppTitleElement.CreateInstance():
                    print('GetSubAppTitleElement: Located SubAppTitleElement: ' + str(Title))
                    return(SubAppTitleElement)
            
        return(None)    
    ...
    
         
    def GetSubAppNavigateUpOrBackElement(self):
    
        def FindSubAppNavigateUpOrBackElement(ElementObject = None):
            
            if ElementObject == None:
                ElementObject = self.SubAppRootNode
            
            if 'class' in ElementObject.Attributes and 'content-desc' in ElementObject.Attributes:
                if  ( ( ElementObject.Attributes['class'] == 'android.widget.ImageButton' ) and
                     ( (ElementObject.Attributes['content-desc'] == 'Navigate up') or
                       (ElementObject.Attributes['content-desc'] == 'Back') ) ):
                            print('FindSubAppNavigateUpOrBackElement: Found SubAppNavigateBackElement')
                            return ElementObject
            
            for ChildObject in ElementObject:
                ElementResult = FindSubAppNavigateUpOrBackElement(ChildObject)                
                if ElementResult != None:
                    return ElementResult
            return(None)
        
        while True:

            SubAppNavigateUpOrBackElement = FindSubAppNavigateUpOrBackElement(
                                            ElementObject = self.SubAppRootNode)
            
            if SubAppNavigateUpOrBackElement != None:
            
                #if SubAppNavigateUpOrBackElement.CreateInstance() ):
                #    print('GetSubAppNavigateUpOrBackElement: Located SubAppNavigateUpOrBackElement: ')
                return(SubAppNavigateUpOrBackElement)
                    
        return(None)                
    ...
'''

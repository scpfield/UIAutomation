import sys, os
from enum import Enum

Driver          = None
App             = None
CurrentPageName = None
CurrentPage     = None
CurrentActivity = None

# app_config.CurrentPage.PageElementTree

class DOMNodeTypes(Enum):

    ELEMENT_NODE                = 1
    ATTRIBUTE_NODE              = 2
    TEXT_NODE                   = 3
    CDATA_SECTION_NODE          = 4
    ENTITY_REFERENCE_NODE       = 5
    ENTITY_NODE                 = 6
    PROCESSING_INSTRUCTION_NODE = 7
    COMMENT_NODE                = 8
    DOCUMENT_NODE               = 9
    DOCUMENT_TYPE_NODE          = 10
    DOCUMENT_FRAGMENT_NODE      = 11
    NOTATION_NODE               = 12
    
    DOCUMENT_POSITION_DISCONNECTED              = 1
    DOCUMENT_POSITION_PRECEDING                 = 2
    DOCUMENT_POSITION_FOLLOWING                 = 4
    DOCUMENT_POSITION_CONTAINS                  = 8
    DOCUMENT_POSITION_CONTAINED_BY              = 16
    DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC   = 32
...


class Container():

    def __iter__( self ):
        #print("iter called")
        self._ChildList = []
        for Key, Value in self.__dict__.items():
            #print("iter key in self dict: " + Key)
            if 'Element' in Value.__class__.__name__:
                self._ChildList.append( Value )
        return self
        
    def __next__( self ):    
        #print("next called")
        if len( self._ChildList ) > 0:
            return self._ChildList.pop( 0 )
        else:
            del self._ChildList
            raise StopIteration
    
    def __len__( self ):
        #print("len called")
        Length = 0
        for Key, Value in self.__dict__.items():
            if 'Element' in Value.__class__.__name__:
                Length += 1
        return Length
        
    def __contains__( self, SubStr ):
        for Key, Value in self.__dict__.items():
            if SubStr in Key:
                return True
        return False
        

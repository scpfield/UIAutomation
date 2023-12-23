# UIAutomation
Python Framework For Non-Flakey UI Automation

Python project that provides a non-flakey framework for developing UI-driven automations with Selenium or Appium for WebApps or Android apps.

Quite a lot is implemented, but still under construction.

There are 3 class hierarchies:

1)  Application base class, extended by either WebApp or MobileApp classes providing highest-level functionality, and are containers for Pages.

2)  Page base class, extended by either WebPages or MobilePages.  These represent either HTML or Android XML pages that users interact with.  They are abstracted into Python Object Trees with all of the elements of the original pages.

3)  Element base class, extended by various UI controls such as buttons or edit fields and wired to an underlying communication provider such as Selenium or Appium, or Chrome CDP, or do-it-yourself.


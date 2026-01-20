
import wx

# Create a new event type
WORKSPACE_ACTIVE_CHANGED_EVENT_TYPE = wx.NewEventType()

# Create a binder
EVT_WORKSPACE_ACTIVE_CHANGED = wx.PyEventBinder(
    WORKSPACE_ACTIVE_CHANGED_EVENT_TYPE, 1)

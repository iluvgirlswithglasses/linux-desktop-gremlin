from ..resources import SpriteProperties as sp
from ..settings import HotspotSettings as hs


def compute_top_hotspot_geometry():
    w = hs.TopHotspotWidth
    h = hs.TopHotspotHeight
    x = (sp.FrameWidth - w) // 2
    y = int(0)
    return (x, y, w, h)


def compute_left_hotspot_geometry():
    w = hs.SideHotspotWidth
    h = hs.SideHotspotHeight
    x = int(0)
    y = (sp.FrameHeight - h) // 2
    return (x, y, w, h)


def compute_right_hotspot_geometry():
    w = hs.SideHotspotWidth
    h = hs.SideHotspotHeight
    x = sp.FrameWidth - w
    y = (sp.FrameHeight - h) // 2
    return (x, y, w, h)

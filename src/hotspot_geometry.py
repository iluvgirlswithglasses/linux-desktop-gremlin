
from . import settings


def compute_top_hotspot_geometry():
    m = settings.SpriteMap
    w = m.TopHotspotWidth
    h = m.TopHotspotHeight
    x = (m.FrameWidth - w) / 2.0
    y = 0.0
    return (x, y, w, h)


def compute_left_hotspot_geometry():
    m = settings.SpriteMap
    w = m.SideHotspotWidth
    h = m.SideHotspotHeight
    x = 0.0
    y = (m.FrameHeight - h) / 2.0
    return (x, y, w, h)


def compute_right_hotspot_geometry():
    m = settings.SpriteMap
    w = m.SideHotspotWidth
    h = m.SideHotspotHeight
    x = m.FrameWidth - w
    y = (m.FrameHeight - h) / 2.0
    return (x, y, w, h)

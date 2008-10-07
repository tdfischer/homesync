import dbus

class DeviceWatcher:
  def __init__(self):
    bus = dbus.SessionBus()
    self.notify = dbus.Interface(bus.get_object("org.freedesktop.Notifications", "/org/freedesktop/Notifications"), "org.freedesktop.Notifications")
    bus = dbus.SystemBus()
    self.hal = dbus.Interface(bus.get_object("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager"), "org.freedesktop.Hal.Manager")
    self.hal.connect_to_signal("DeviceAdded", self.newDevice)
    
  def newDevice(self, udi):
    print "New device: %s"%(udi)
    bus = dbus.SystemBus()
    device = dbus.Interface(bus.get_object("org.freedesktop.Hal", udi), "org.freedesktop.Hal.Device")
    try:
      capabilities = device.GetProperty("info.capabilities")
    except:
      return
    if "volume" in capabilities:
      size = device.GetProperty("volume.size")/1024/1024/1024
      if (size>0):
        self.notify.Notify(
          "HomeSync",
          0,
          "/usr/share/icons/oxygen/48x48/devices/drive-removable-media.png",
          "Use 'iAUDIO' to store HomeSync backups?",
          "You connected the 'iAUDIO' device to your computer. It has enough free space (%i GB) to be used as a place to store your HomeSync backups. Do you want to use it now?\n\nYou can also set up devices later through the control panel."%(size),
          ("yes","Yes","no","No"),
          {},
          0)
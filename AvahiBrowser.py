class AvahiBrowser:
  def __init__(self):
    self.name = dbus.service.BusName("net.wm161.HomeSync",bus=dbus.SessionBus())
    bus = dbus.SystemBus()
    self.avahi = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), avahi.DBUS_INTERFACE_SERVER)
    
    self.avahiGroup = dbus.Interface(bus.get_object(avahi.DBUS_NAME, self.avahi.EntryGroupNew()), avahi.DBUS_INTERFACE_ENTRY_GROUP)
    
    self.avahiGroup.AddService(
      avahi.IF_UNSPEC,
      avahi.PROTO_UNSPEC,
      dbus.UInt32(0),
      "HomeSync Server",
      "_git._tcp",
      "","",
      dbus.UInt16(9418),
      avahi.dict_to_txt_array({"HomeSync":1,"UID":500}))
    self.avahiGroup.Commit()
    
    self.browser = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
      self.avahi.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, '_git._tcp', 'local', dbus.UInt32(0))),
      avahi.DBUS_INTERFACE_SERVICE_BROWSER)
    self.browser.connect_to_signal("ItemNew", self.discoveredServer)
  
  def discoveredServer(self, interface, protocol, name, stype, domain, flags):
    print "Found service '%s' type '%s' domain '%s' " % (name, stype, domain)
    if flags & avahi.LOOKUP_RESULT_LOCAL:
      # local service, skip
      pass
    self.avahi.ResolveService(interface, protocol, name, stype, 
      domain, avahi.PROTO_UNSPEC, dbus.UInt32(0), 
      reply_handler=self.resolvedServer, error_handler=self.resolveFailed)

  def resolveFailed(self, *args):
    print args[0]

  def resolvedServer(self, *args):
    print 'service resolved'
    print 'name:', args[2]
    print 'address:', args[7]
    print 'port:', args[8]
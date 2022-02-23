/*
This scenario just connect the containers through a simple point-2-point
link.

For testing delay has been added to CSMA and point-to-point links.
*/

#include <iostream>
#include <fstream>

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/wifi-module.h"
#include "ns3/csma-module.h"
#include "ns3/internet-module.h"
#include "ns3/ipv4-global-routing-helper.h"
#include "ns3/tap-bridge-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("TapCsmaDocker");

int main(int argc, char *argv[])
{
  // LogComponentEnable("TapBridge", LOG_LEVEL_INFO);
  std::string mode = "ConfigureLocal";
  std::string tapName = "ns3tap";

  GlobalValue::Bind("SimulatorImplementationType", StringValue("ns3::RealtimeSimulatorImpl"));
  GlobalValue::Bind("ChecksumEnabled", BooleanValue(true));

  NodeContainer nodes;
  nodes.Create(4);

  PointToPointHelper pointToPoint;
  pointToPoint.SetDeviceAttribute("DataRate", StringValue("100Mbps")); // BW
  pointToPoint.SetChannelAttribute("Delay", StringValue("15ms"));      // delay

  CsmaHelper csma;
  csma.SetChannelAttribute("DataRate", StringValue("100Gbps"));
  csma.SetChannelAttribute("Delay", StringValue("5ms"));

  NetDeviceContainer csmaDevIn = csma.Install(NodeContainer{nodes.Get(0), nodes.Get(1)});
  NetDeviceContainer p2pDev = pointToPoint.Install(NodeContainer{nodes.Get(1), nodes.Get(2)});
  NetDeviceContainer csmaDevOut = csma.Install(NodeContainer{nodes.Get(3), nodes.Get(2)});

  InternetStackHelper stack;
  stack.Install(NodeContainer{nodes.Get(1), nodes.Get(2)});

  Ipv4AddressHelper addressesCsmaIn;
  addressesCsmaIn.SetBase("10.1.0.0", "255.255.255.0", "0.0.0.3");
  Ipv4AddressHelper addressesP2p;
  addressesP2p.SetBase("11.0.0.0", "255.255.255.0", "0.0.0.1");
  Ipv4AddressHelper addressesCsmaOut;
  addressesCsmaOut.SetBase("10.2.0.0", "255.255.255.0", "0.0.0.3");

  Ipv4InterfaceContainer ifacesCsmaIn = addressesCsmaIn.Assign({csmaDevIn.Get(1)});
  Ipv4InterfaceContainer ifacesP2p = addressesP2p.Assign(p2pDev);
  Ipv4InterfaceContainer ifacesCsmaOut = addressesCsmaOut.Assign({csmaDevOut.Get(1)});

  {
    TapBridgeHelper tapBridge;
    tapBridge.SetAttribute("Mode", StringValue("UseBridge"));
    tapBridge.SetAttribute("DeviceName", StringValue("tap-left"));
    tapBridge.Install(nodes.Get(0), csmaDevIn.Get(0));
  }
  {
    TapBridgeHelper tapBridge;
    tapBridge.SetAttribute("Mode", StringValue("UseBridge"));
    tapBridge.SetAttribute("DeviceName", StringValue("tap-right"));
    tapBridge.Install(nodes.Get(3), csmaDevOut.Get(0));
  }
  Ipv4GlobalRoutingHelper::PopulateRoutingTables();

  // // Simulator::Stop(Seconds(60.));
  Simulator::Run();
  Simulator::Destroy();
}
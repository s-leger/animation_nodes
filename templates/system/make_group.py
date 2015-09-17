import bpy
from ... base_types.template import Template

class MakeGroupTemplateOperator(bpy.types.Operator, Template):
    bl_idname = "an.make_group_template_operator"
    bl_label = "Make Group"

    def insert(self):
        nodes = self.selectedNodes

        if not self.areNetworksCompatible(nodes):
            self.report(type = {"INFO"}, message = "The node networks are not compatible")
            return

        if self.areThereInvalidDependencies(nodes):
            self.report(type = {"INFO"}, message = "There are invalid node dependencies")

        groupInputNode = self.newNode("an_GroupInputNode", x = 0, y = 0)
        for socket in self.getGroupInputSockets(nodes):
            groupInputNode.newParameter(socket.dataType, name = socket.getDisplayedName())

        groupOutputNode = self.newNode("an_GroupOutputNode", x = 300, y = 0)
        groupOutputNode.groupInputIdentifier = groupInputNode.identifier
        for socket in self.getGroupOutputSockets(nodes):
            groupOutputNode.newReturn(socket.dataType, name = socket.getDisplayedName())

    def areNetworksCompatible(self, nodes):
        networks = set(node.network for node in nodes if hasattr(node, "isAnimationNode"))

        subNetworkIdentifiers = set()
        mainNetworkAmount = 0
        invalidNetworkAmount = 0
        for network in networks:
            if network.isSubnetwork: subNetworkIdentifiers.add(network.identifier)
            if network.type == "Main": mainNetworkAmount += 1
            if network.type == "Invalid": invalidNetworkAmount += 1

        if invalidNetworkAmount > 0: return False
        if mainNetworkAmount == len(networks): return True
        if len(subNetworkIdentifiers) == 1 and mainNetworkAmount == 0: return True
        return False

    def areThereInvalidDependencies(self, nodes):
        dependencyNodes = set()
        for node in nodes:
            dependencyNodes.update(node.getNodesWhenFollowingLinks(followInputs = True))

        dependentNodes = set()
        for node in nodes:
            dependentNodes.update(node.getNodesWhenFollowingLinks(followOutputs = True))

        unfilteredInvalidNodes = dependencyNodes.intersection(dependentNodes)
        invalidNodes = unfilteredInvalidNodes.difference(nodes)
        return len(invalidNodes) > 0

    def getGroupInputSockets(self, nodes):
        sockets = set()
        for node in nodes:
            if not hasattr(node, "isAnimationNode"): continue
            for socket in node.inputs:
                origin = socket.dataOrigin
                if origin is not None:
                    if origin.node not in nodes: sockets.add(socket)
        return list(sockets)

    def getGroupOutputSockets(self, nodes):
        sockets = set()
        for node in nodes:
            if not hasattr(node, "isAnimationNode"): continue
            for socket in node.outputs:
                for target in socket.dataTargets:
                    if target.node not in nodes: sockets.add(socket)
        return sockets

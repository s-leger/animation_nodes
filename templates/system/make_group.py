import bpy
from mathutils import Vector
from ... base_types.template import Template

class MakeGroupTemplateOperator(bpy.types.Operator, Template):
    bl_idname = "an.make_group_template_operator"
    bl_label = "Make Group"

    def insert(self):
        nodes = self.selectedNodes

        if not self.canNodesBeInASubprogram(nodes):
            self.report(type = {"INFO"}, message = "At least one node cannot be in a subprogram")
            return

        if not self.areNetworksCompatible(nodes):
            self.report(type = {"INFO"}, message = "The node networks are not compatible")
            return

        if self.areThereInvalidDependencies(nodes):
            self.report(type = {"INFO"}, message = "There are invalid node dependencies")
            return

        inputConnections = self.getGroupInputConnections(nodes)
        outputConnections = self.getGroupOutputConnections(nodes)

        if len(inputConnections) + len(outputConnections) == 0:
            self.report(type = {"INFO"}, message = "The selected nodes must have at least one link to the outside")
            return

        selectedNodesCenter = self.getAverageLocation(nodes)
        minXBoundary, maxXBoundary = self.getHorizontalNodeBoundaries(nodes)

        groupInputNode = self.newNode("an_GroupInputNode", applyCursorOffset = False)
        groupInputNode.location = (minXBoundary - 300, selectedNodesCenter.y)
        for socket, origin in inputConnections:
            groupInputNode.newParameter(socket.dataType, name = socket.getDisplayedName())

        groupOutputNode = self.newNode("an_GroupOutputNode", applyCursorOffset = False)
        groupOutputNode.groupInputIdentifier = groupInputNode.identifier
        groupOutputNode.location = (maxXBoundary + 300, selectedNodesCenter.y)
        for socket, target in outputConnections:
            groupOutputNode.newReturn(socket.dataType, name = socket.getDisplayedName())

        for link in self.nodeTree.links:
            if self.shouldLinkBeRemoved(link, inputConnections, outputConnections):
                self.nodeTree.links.remove(link)

        invokeSubprogramNode = self.newNode("an_InvokeSubprogramNode", move = False, applyCursorOffset = False)
        invokeSubprogramNode.location = selectedNodesCenter
        invokeSubprogramNode.subprogramIdentifier = groupInputNode.identifier

        self.updateSubprograms()

        for i, socket in enumerate(invokeSubprogramNode.inputs):
            socket.linkWith(inputConnections[i][1])
        for i, socket in enumerate(invokeSubprogramNode.outputs):
            socket.linkWith(outputConnections[i][1])

        for i, socket in enumerate(groupInputNode.outputs[:-1]):
            socket.linkWith(inputConnections[i][0])

        for i, socket in enumerate(groupOutputNode.inputs[:-1]):
            socket.linkWith(outputConnections[i][0])

        self.move(*nodes)


    def shouldLinkBeRemoved(self, link, inputConnections, outputConnections):
        for socket, origin in inputConnections:
            if link.to_socket == socket and link.from_socket == origin:
                return True
        for socket, target in outputConnections:
            if link.from_socket == socket and link.to_socket == target:
                return True
        return False

    def getAverageLocation(self, nodes):
        location = Vector((0, 0))
        for node in nodes:
            location += node.location
        print(location)
        return location / len(nodes)

    def getHorizontalNodeBoundaries(self, nodes):
        minX = min([node.location.x for node in nodes])
        maxX = max([node.location.x for node in nodes])
        return minX, maxX

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

    def canNodesBeInASubprogram(self, nodes):
        for node in nodes:
            if not node.isAnimationNode: continue
            if "No Subprogram" in node.options: return False
        return True

    def getGroupInputConnections(self, nodes):
        connections = []
        for node in nodes:
            if not node.isAnimationNode: continue
            for socket in node.inputs:
                origin = socket.dataOrigin
                if origin is not None:
                    if origin.node not in nodes:
                        connections.append((socket, origin))
        return connections

    def getGroupOutputConnections(self, nodes):
        connections = []
        for node in nodes:
            if not node.isAnimationNode: continue
            for socket in node.outputs:
                for target in socket.dataTargets:
                    if target.node not in nodes:
                        connections.append((socket, target))
        return connections

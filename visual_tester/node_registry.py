from node_type import NodeCategory, NodeGroup, NodeType
from node_pin import NodePin, PinType


class NodeRegistry:
    _types: dict[str, NodeType] = {}

    @classmethod
    def register(cls, name: str, node_type: NodeType):
        cls._types[name] = node_type

    @classmethod
    def get(cls, name: str) -> NodeType:
        return cls._types[name]

    @classmethod
    def all(cls):
        return cls._types.items()


def register_default_nodes():
    NodeRegistry.register("Start", NodeType(
        title="Start",
        node_group=NodeGroup.EVENT,
        inputs=[],
        outputs=[NodePin("Exec",
                         pin_type=PinType.EXECUTE,
                         colour=(255, 255, 255))],
        colour=(200, 60, 60),
        category=NodeCategory.START,
    ))

    NodeRegistry.register("Condition", NodeType(
        title="Condition",
        node_group=NodeGroup.FLOW_CONTROL,
        inputs=[NodePin("In", pin_type=PinType.EXECUTE)],
        outputs=[
            NodePin("True", pin_type=PinType.EXECUTE),
            NodePin("False", pin_type=PinType.EXECUTE)
        ],
        colour=(70, 70, 80),
    ))

    NodeRegistry.register("Action", NodeType(
        title="Action",
        node_group=NodeGroup.ACTION,
        inputs=[NodePin("Trigger", pin_type=PinType.EXECUTE)],
        outputs=[NodePin("Done", pin_type=PinType.EXECUTE)],
        colour=(90, 60, 120),
    ))

    NodeRegistry.register("Combiner", NodeType(
        title="Combiner",
        node_group=NodeGroup.FLOW_CONTROL,
        inputs=[NodePin("Input", pin_type=PinType.EXECUTE)],
        outputs=[NodePin("Output", pin_type=PinType.EXECUTE)],
        can_add_inputs=True,
        colour=(90, 60, 120),
    ))

    NodeRegistry.register("Splitter", NodeType(
        title="Splitter",
        node_group=NodeGroup.FLOW_CONTROL,
        inputs=[NodePin("Input", pin_type=PinType.EXECUTE)],
        outputs=[NodePin("Out", pin_type=PinType.EXECUTE)],
        can_add_outputs=True,
        colour=(90, 60, 120),
    ))

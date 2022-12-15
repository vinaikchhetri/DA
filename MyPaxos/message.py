from dataclasses import dataclass, field

@dataclass
class message:
    instance_index: int = -1
    phase: str = None
    c_rnd: int = 0
    c_val: int = None
    rnd: int = 0
    v_rnd: int = 0
    v_val: int = None
    client_val: int = None
    decisions: dict = field(default_factory=dict)
    # pid: int = None
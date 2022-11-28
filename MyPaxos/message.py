from dataclasses import dataclass

@dataclass
class message:
    phase: str = None
    c_rnd: int = 0
    c_val: int = None
    rnd: int = 0
    v_rnd: int = 0
    v_val: int = None
    client_val: int = None
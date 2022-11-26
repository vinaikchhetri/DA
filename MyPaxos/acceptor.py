class acceptor:
    def __init__(self, rnd, v_rnd, v_val):
        self.rnd = rnd
        self.v_rnd = v_rnd
        self.v_val = v_val
    def __str__(self):
        return f"Acceptor-> rnd:{self.rnd} v-rnd:{self.v_rnd} v_val:{self.v_val}"
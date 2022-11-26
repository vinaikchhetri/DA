class proposer:
    def __init__(self, c_rnd, c_val):
        self.c_rnd = c_rnd
        self.c_val = c_val
        
    def __str__(self):
        return f"Proposer-> c_rnd:{self.c_rnd} c_val:{self.c_val}"
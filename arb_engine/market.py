import math
from datetime import datetime, timezone
from .models import Quote
class SimMarket:
    def __init__(self,venue,phase): self.venue=venue; self.phase=phase; self.tick=0
    async def quote(self,symbol):
        self.tick+=1
        base=3000+math.sin((self.tick+self.phase)/3)*4
        mid=base+{'CEX_A':-2,'CEX_B':2,'DEX_A':0}.get(self.venue,0)
        return Quote(self.venue,symbol,mid-.4,mid+.4,10,10,10 if self.venue.startswith('CEX') else 30,2 if self.venue=='DEX_A' else 0,datetime.now(timezone.utc))
